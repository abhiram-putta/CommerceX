"""
WebSocket endpoints for real-time communication.
"""
import asyncio
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from fastapi.exceptions import HTTPException
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.config.settings import get_settings
from app.core.websocket import manager
from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


async def get_current_user_from_token(token: str, db: AsyncSession):
    """
    Verify JWT token and get current user for WebSocket.

    Args:
        token: JWT token
        db: Database session

    Returns:
        User instance or None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None

        user_repo = UserRepository(db)
        user = await user_repo.get(UUID(user_id))
        return user
    except JWTError:
        return None


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time notifications.

    Connect to receive instant notifications without polling.

    **Authentication**: Pass JWT token as query parameter
    **URL**: `/ws/notifications?token=YOUR_JWT_TOKEN`

    **Message Format**:
    ```json
    {
      "type": "notification",
      "data": {
        "id": "uuid",
        "title": "Order Shipped",
        "message": "Your order #12345 has been shipped",
        "notification_type": "ORDER_UPDATE",
        "created_at": "2024-01-01T12:00:00Z"
      }
    }
    ```
    """
    # Authenticate user
    user = await get_current_user_from_token(token, db)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, "notifications", user_id=user.id)

    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "connection",
            "message": "Connected to notifications",
            "user_id": str(user.id)
        }, websocket)

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()

            # Handle ping/pong for keepalive
            if data == "ping":
                await manager.send_personal_message({"type": "pong"}, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, "notifications", user_id=user.id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, "notifications", user_id=user.id)


@router.websocket("/ws/orders/{order_id}")
async def websocket_order_tracking(
    websocket: WebSocket,
    order_id: UUID,
    token: str = Query(..., description="JWT access token"),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time order tracking.

    Connect to receive live updates about a specific order.

    **Authentication**: Pass JWT token as query parameter
    **URL**: `/ws/orders/{order_id}?token=YOUR_JWT_TOKEN`

    **Message Format**:
    ```json
    {
      "type": "order_update",
      "data": {
        "order_id": "uuid",
        "status": "SHIPPED",
        "location": "Mumbai Distribution Center",
        "timestamp": "2024-01-01T12:00:00Z",
        "message": "Your order is out for delivery"
      }
    }
    ```
    """
    # Authenticate user
    user = await get_current_user_from_token(token, db)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Verify user owns the order
    order_repo = OrderRepository(db)
    order = await order_repo.get(order_id)

    if not order or order.customer_id != user.id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, "orders", user_id=user.id, resource_id=order_id)

    try:
        # Send current order status
        await manager.send_personal_message({
            "type": "connection",
            "message": f"Connected to order {order_id} tracking",
            "data": {
                "order_id": str(order_id),
                "current_status": order.status.value,
                "order_number": order.order_number
            }
        }, websocket)

        # Keep connection alive
        while True:
            data = await websocket.receive_text()

            if data == "ping":
                await manager.send_personal_message({"type": "pong"}, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, "orders", user_id=user.id, resource_id=order_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, "orders", user_id=user.id, resource_id=order_id)


@router.websocket("/ws/inventory")
async def websocket_inventory_updates(
    websocket: WebSocket,
    product_ids: str = Query(None, description="Comma-separated product IDs to watch"),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for live inventory updates.

    Connect to receive real-time stock updates for products.

    **URL**: `/ws/inventory?product_ids=uuid1,uuid2,uuid3`

    **Message Format**:
    ```json
    {
      "type": "stock_update",
      "data": {
        "product_id": "uuid",
        "product_name": "iPhone 14 Pro",
        "old_stock": 10,
        "new_stock": 5,
        "timestamp": "2024-01-01T12:00:00Z"
      }
    }
    ```

    **Note**: No authentication required for public inventory updates
    """
    await manager.connect(websocket, "inventory")

    # Parse product IDs if provided
    watching_products = []
    if product_ids:
        try:
            watching_products = [UUID(pid.strip()) for pid in product_ids.split(',')]
        except ValueError:
            await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
            return

    try:
        # Send connection confirmation
        await manager.send_personal_message({
            "type": "connection",
            "message": "Connected to inventory updates",
            "watching_products": [str(pid) for pid in watching_products]
        }, websocket)

        # Keep connection alive
        while True:
            data = await websocket.receive_text()

            if data == "ping":
                await manager.send_personal_message({"type": "pong"}, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, "inventory")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, "inventory")


@router.get("/ws/status")
async def get_websocket_status():
    """
    Get WebSocket connection statistics.

    Returns:
    - Total active connections
    - Connections by type
    - System health
    """
    return {
        "total_connections": manager.get_connection_count(),
        "connections_by_type": {
            "notifications": manager.get_connection_count("notifications"),
            "orders": manager.get_connection_count("orders"),
            "inventory": manager.get_connection_count("inventory"),
        },
        "status": "healthy"
    }
