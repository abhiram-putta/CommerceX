"""
Admin dashboard API endpoints.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.services.admin_service import AdminService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_admin_service(db: AsyncSession = Depends(get_db)) -> AdminService:
    """Get admin service instance."""
    return AdminService(
        order_repository=OrderRepository(db),
        product_repository=ProductRepository(db),
        user_repository=UserRepository(db),
        inventory_repository=InventoryRepository(db),
        analytics_repository=AnalyticsRepository(db),
    )


@router.get("/dashboard/overview")
async def get_dashboard_overview(
    current_user: User = Depends(get_current_active_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    Get dashboard overview with key metrics.

    Returns:
    - Total sales
    - Total revenue
    - Total orders
    - Total customers
    - Active products
    - Low stock items count
    - Recent orders
    - Top selling products
    """
    # TODO: Add admin role check
    # if current_user.role != UserRole.ADMIN:
    #     raise ForbiddenError("Admin access required")

    overview = await admin_service.get_dashboard_overview()
    return overview


@router.get("/dashboard/sales")
async def get_sales_metrics(
    period: str = Query("7d", description="Period: 24h, 7d, 30d, 90d, 1y"),
    current_user: User = Depends(get_current_active_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    Get sales metrics for specified period.

    Returns:
    - Total sales
    - Total revenue
    - Average order value
    - Daily breakdown
    - Growth percentage
    """
    metrics = await admin_service.get_sales_metrics(period)
    return metrics


@router.get("/dashboard/revenue")
async def get_revenue_metrics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_active_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    Get revenue metrics with breakdown.

    Returns:
    - Total revenue
    - Revenue by payment method
    - Revenue by order type
    - Daily revenue chart data
    """
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()

    metrics = await admin_service.get_revenue_metrics(start_date, end_date)
    return metrics


@router.get("/dashboard/products")
async def get_product_metrics(
    current_user: User = Depends(get_current_active_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    Get product metrics and insights.

    Returns:
    - Total products
    - Active products
    - Top selling products
    - Low stock products
    - Out of stock products
    - Products by category
    """
    metrics = await admin_service.get_product_metrics()
    return metrics


@router.get("/dashboard/customers")
async def get_customer_metrics(
    period: str = Query("30d", description="Period: 7d, 30d, 90d, 1y"),
    current_user: User = Depends(get_current_active_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    Get customer metrics and analytics.

    Returns:
    - Total customers
    - New customers in period
    - Active customers
    - Customer growth rate
    - Customers by role
    - Top customers by spending
    """
    metrics = await admin_service.get_customer_metrics(period)
    return metrics


@router.get("/dashboard/orders")
async def get_order_metrics(
    period: str = Query("7d", description="Period: 24h, 7d, 30d, 90d"),
    current_user: User = Depends(get_current_active_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    Get order metrics and status distribution.

    Returns:
    - Total orders
    - Orders by status
    - Pending orders
    - Completed orders
    - Cancelled orders
    - Average processing time
    """
    metrics = await admin_service.get_order_metrics(period)
    return metrics


@router.get("/dashboard/inventory")
async def get_inventory_metrics(
    current_user: User = Depends(get_current_active_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    Get inventory health metrics.

    Returns:
    - Total stock value
    - Low stock items
    - Out of stock items
    - Stock alerts
    - Inventory turnover
    """
    metrics = await admin_service.get_inventory_metrics()
    return metrics


@router.get("/dashboard/recent-activity")
async def get_recent_activity(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    Get recent activity feed.

    Returns:
    - Recent orders
    - Recent customers
    - Recent reviews
    - Recent low stock alerts
    """
    activity = await admin_service.get_recent_activity(limit)
    return activity


@router.get("/dashboard/performance")
async def get_performance_kpis(
    current_user: User = Depends(get_current_active_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    Get key performance indicators (KPIs).

    Returns:
    - Conversion rate
    - Average order value
    - Customer lifetime value
    - Cart abandonment rate
    - Product return rate
    - Customer satisfaction score
    """
    kpis = await admin_service.get_performance_kpis()
    return kpis


@router.get("/dashboard/top-products")
async def get_top_products(
    period: str = Query("30d", description="Period: 7d, 30d, 90d, 1y"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    Get top selling products.

    Returns list of products sorted by:
    - Units sold
    - Revenue generated
    - With sales data
    """
    products = await admin_service.get_top_products(period, limit)
    return products


@router.get("/dashboard/alerts")
async def get_dashboard_alerts(
    current_user: User = Depends(get_current_active_user),
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    Get dashboard alerts and notifications.

    Returns:
    - Low stock alerts
    - Out of stock alerts
    - Pending orders count
    - Pending returns count
    - Failed payments count
    """
    alerts = await admin_service.get_dashboard_alerts()
    return alerts
