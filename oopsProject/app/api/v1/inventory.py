"""
Inventory management endpoints for sellers.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, require_seller
from app.config.database import get_db
from app.models.user import User
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.common import MessageResponse
from app.schemas.inventory import InventoryCreate, InventoryResponse, InventoryUpdate

router = APIRouter()


def get_inventory_repository(db: AsyncSession = Depends(get_db)) -> InventoryRepository:
    """Get inventory repository dependency."""
    return InventoryRepository(db)


@router.get("", response_model=List[InventoryResponse])
async def get_my_inventory(
    available_only: bool = Query(False, description="Only show items with stock > 0"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_seller),
    inventory_repo: InventoryRepository = Depends(get_inventory_repository),
) -> List[InventoryResponse]:
    """
    Get inventory for current seller.

    - **available_only**: Filter for items with stock > 0
    - **page**: Page number
    - **page_size**: Items per page

    Returns all inventory entries owned by the current seller.
    """
    skip = (page - 1) * page_size
    inventory_items = await inventory_repo.get_by_owner(
        owner_id=current_user.id,
        available_only=available_only
    )

    # Apply pagination
    paginated_items = inventory_items[skip:skip + page_size]
    return [InventoryResponse.model_validate(item) for item in paginated_items]


@router.get("/product/{product_id}", response_model=InventoryResponse)
async def get_my_product_inventory(
    product_id: UUID,
    current_user: User = Depends(require_seller),
    inventory_repo: InventoryRepository = Depends(get_inventory_repository),
) -> InventoryResponse:
    """
    Get inventory for a specific product owned by current seller.

    - **product_id**: Product UUID

    Returns the inventory entry for this product-seller combination.
    """
    inventory = await inventory_repo.get_by_product_and_owner(
        product_id=product_id,
        owner_id=current_user.id
    )

    if not inventory:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Inventory not found for this product")

    return InventoryResponse.model_validate(inventory)


@router.post("", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory(
    inventory_data: InventoryCreate,
    current_user: User = Depends(require_seller),
    inventory_repo: InventoryRepository = Depends(get_inventory_repository),
    db: AsyncSession = Depends(get_db),
) -> InventoryResponse:
    """
    Create new inventory entry.

    - **product_id**: Product UUID
    - **stock_quantity**: Available stock
    - **price**: Selling price
    - **min_order_quantity**: Minimum order quantity (default: 1)
    - **max_order_quantity**: Maximum order quantity (optional)

    Creates inventory for a product at your store/warehouse.
    """
    # Verify product exists
    product_repo = ProductRepository(db)
    product = await product_repo.get(inventory_data.product_id)

    if not product:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Product not found")

    # Check if inventory already exists
    existing = await inventory_repo.get_by_product_and_owner(
        product_id=inventory_data.product_id,
        owner_id=current_user.id
    )

    if existing:
        from app.core.exceptions import BadRequestError
        raise BadRequestError("Inventory already exists for this product. Use update instead.")

    # Create inventory
    inventory_dict = inventory_data.model_dump()
    inventory_dict['owner_id'] = current_user.id
    inventory_dict['owner_type'] = current_user.role

    inventory = await inventory_repo.create(inventory_dict)

    return InventoryResponse.model_validate(inventory)


@router.put("/{inventory_id}", response_model=InventoryResponse)
async def update_inventory(
    inventory_id: UUID,
    inventory_data: InventoryUpdate,
    current_user: User = Depends(require_seller),
    inventory_repo: InventoryRepository = Depends(get_inventory_repository),
) -> InventoryResponse:
    """
    Update inventory entry.

    - **inventory_id**: Inventory UUID
    - **stock_quantity**: New stock quantity (optional)
    - **price**: New price (optional)
    - **min_order_quantity**: New minimum order (optional)
    - **max_order_quantity**: New maximum order (optional)

    Only the inventory owner can update it.
    """
    inventory = await inventory_repo.get(inventory_id)

    if not inventory:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Inventory not found")

    # Verify ownership
    if inventory.owner_id != current_user.id:
        from app.core.exceptions import BadRequestError
        raise BadRequestError("Unauthorized to update this inventory")

    # Update inventory
    update_dict = inventory_data.model_dump(exclude_unset=True)
    updated_inventory = await inventory_repo.update(inventory_id, update_dict)

    return InventoryResponse.model_validate(updated_inventory)


@router.put("/{inventory_id}/stock", response_model=InventoryResponse)
async def update_stock_quantity(
    inventory_id: UUID,
    quantity_change: int = Query(..., description="Amount to add/subtract (use negative for decrease)"),
    current_user: User = Depends(require_seller),
    inventory_repo: InventoryRepository = Depends(get_inventory_repository),
) -> InventoryResponse:
    """
    Update stock quantity by adding or subtracting.

    - **inventory_id**: Inventory UUID
    - **quantity_change**: Amount to change (positive to add, negative to subtract)

    Example:
    - quantity_change=100 → Adds 100 units
    - quantity_change=-50 → Removes 50 units

    Useful for stock replenishment or manual adjustments.
    """
    inventory = await inventory_repo.get(inventory_id)

    if not inventory:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Inventory not found")

    # Verify ownership
    if inventory.owner_id != current_user.id:
        from app.core.exceptions import BadRequestError
        raise BadRequestError("Unauthorized to update this inventory")

    # Update stock
    updated_inventory = await inventory_repo.update_stock(inventory_id, quantity_change)

    return InventoryResponse.model_validate(updated_inventory)


@router.delete("/{inventory_id}", response_model=MessageResponse)
async def delete_inventory(
    inventory_id: UUID,
    current_user: User = Depends(require_seller),
    inventory_repo: InventoryRepository = Depends(get_inventory_repository),
) -> MessageResponse:
    """
    Delete inventory entry.

    - **inventory_id**: Inventory UUID

    Only the inventory owner can delete it.
    This removes the product from your inventory.
    """
    inventory = await inventory_repo.get(inventory_id)

    if not inventory:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Inventory not found")

    # Verify ownership
    if inventory.owner_id != current_user.id:
        from app.core.exceptions import BadRequestError
        raise BadRequestError("Unauthorized to delete this inventory")

    # Delete inventory
    success = await inventory_repo.delete(inventory_id)

    if not success:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Inventory not found")

    return MessageResponse(message="Inventory deleted successfully")


@router.get("/low-stock", response_model=List[InventoryResponse])
async def get_low_stock_items(
    threshold: int = Query(10, ge=1, description="Stock threshold"),
    current_user: User = Depends(require_seller),
    inventory_repo: InventoryRepository = Depends(get_inventory_repository),
) -> List[InventoryResponse]:
    """
    Get inventory items with low stock.

    - **threshold**: Stock level threshold (default: 10)

    Returns all inventory items where stock_quantity <= threshold.
    Useful for reordering alerts.
    """
    all_inventory = await inventory_repo.get_by_owner(
        owner_id=current_user.id,
        available_only=False
    )

    # Filter for low stock
    low_stock_items = [
        item for item in all_inventory
        if item.stock_quantity <= threshold
    ]

    return [InventoryResponse.model_validate(item) for item in low_stock_items]
