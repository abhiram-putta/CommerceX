"""
WebSocket connection manager for real-time features.
"""
import json
from typing import Dict, List, Set
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time communication.
    Supports multiple connection types: orders, notifications, inventory.
    """

    def __init__(self):
        """Initialize connection manager."""
        # Store active connections by type
        self.active_connections: Dict[str, List[WebSocket]] = {
            'notifications': [],
            'orders': [],
            'inventory': [],
        }

        # Store user-specific connections
        self.user_connections: Dict[UUID, List[WebSocket]] = {}

        # Store order-specific connections
        self.order_connections: Dict[UUID, List[WebSocket]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        connection_type: str,
        user_id: UUID = None,
        resource_id: UUID = None
    ):
        """
        Accept and register a new WebSocket connection.

        Args:
            websocket: WebSocket instance
            connection_type: Type of connection (notifications, orders, etc.)
            user_id: Optional user ID for user-specific connections
            resource_id: Optional resource ID (e.g., order_id)
        """
        await websocket.accept()

        # Add to general connections
        if connection_type not in self.active_connections:
            self.active_connections[connection_type] = []
        self.active_connections[connection_type].append(websocket)

        # Add to user-specific connections
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)

        # Add to resource-specific connections (e.g., order tracking)
        if resource_id:
            if resource_id not in self.order_connections:
                self.order_connections[resource_id] = []
            self.order_connections[resource_id].append(websocket)

        logger.info(
            f"WebSocket connected: type={connection_type}, "
            f"user_id={user_id}, resource_id={resource_id}"
        )

    def disconnect(
        self,
        websocket: WebSocket,
        connection_type: str,
        user_id: UUID = None,
        resource_id: UUID = None
    ):
        """
        Remove a WebSocket connection.

        Args:
            websocket: WebSocket instance
            connection_type: Type of connection
            user_id: Optional user ID
            resource_id: Optional resource ID
        """
        # Remove from general connections
        if connection_type in self.active_connections:
            if websocket in self.active_connections[connection_type]:
                self.active_connections[connection_type].remove(websocket)

        # Remove from user-specific connections
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        # Remove from resource-specific connections
        if resource_id and resource_id in self.order_connections:
            if websocket in self.order_connections[resource_id]:
                self.order_connections[resource_id].remove(websocket)
            if not self.order_connections[resource_id]:
                del self.order_connections[resource_id]

        logger.info(
            f"WebSocket disconnected: type={connection_type}, "
            f"user_id={user_id}, resource_id={resource_id}"
        )

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send a message to a specific WebSocket connection.

        Args:
            message: Message dict to send
            websocket: Target WebSocket
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast_to_type(self, message: dict, connection_type: str):
        """
        Broadcast message to all connections of a specific type.

        Args:
            message: Message dict to broadcast
            connection_type: Type of connections to broadcast to
        """
        if connection_type not in self.active_connections:
            return

        disconnected = []
        for connection in self.active_connections[connection_type]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)

        # Remove disconnected connections
        for conn in disconnected:
            self.active_connections[connection_type].remove(conn)

    async def broadcast_to_user(self, message: dict, user_id: UUID):
        """
        Send message to all connections of a specific user.

        Args:
            message: Message dict to send
            user_id: Target user ID
        """
        if user_id not in self.user_connections:
            return

        disconnected = []
        for connection in self.user_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to user {user_id}: {e}")
                disconnected.append(connection)

        # Remove disconnected connections
        for conn in disconnected:
            self.user_connections[user_id].remove(conn)

    async def broadcast_to_order(self, message: dict, order_id: UUID):
        """
        Send message to all connections watching a specific order.

        Args:
            message: Message dict to send
            order_id: Target order ID
        """
        if order_id not in self.order_connections:
            return

        disconnected = []
        for connection in self.order_connections[order_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to order {order_id}: {e}")
                disconnected.append(connection)

        # Remove disconnected connections
        for conn in disconnected:
            self.order_connections[order_id].remove(conn)

    def get_connection_count(self, connection_type: str = None) -> int:
        """
        Get count of active connections.

        Args:
            connection_type: Optional type filter

        Returns:
            Number of active connections
        """
        if connection_type:
            return len(self.active_connections.get(connection_type, []))
        return sum(len(conns) for conns in self.active_connections.values())

    def get_user_connection_count(self, user_id: UUID) -> int:
        """
        Get count of connections for a specific user.

        Args:
            user_id: User ID

        Returns:
            Number of user's active connections
        """
        return len(self.user_connections.get(user_id, []))


# Global connection manager instance
manager = ConnectionManager()
