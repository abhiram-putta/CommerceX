"""
Admin service for dashboard metrics and analytics.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any

from sqlalchemy import func, select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import Inventory
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.utils.enums import OrderStatus, PaymentStatus
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AdminService:
    """Service for admin dashboard and metrics."""

    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        user_repository: UserRepository,
        inventory_repository: InventoryRepository,
        analytics_repository: AnalyticsRepository,
    ):
        self.order_repo = order_repository
        self.product_repo = product_repository
        self.user_repo = user_repository
        self.inventory_repo = inventory_repository
        self.analytics_repo = analytics_repository

    async def get_dashboard_overview(self) -> Dict[str, Any]:
        """
        Get comprehensive dashboard overview.

        Returns:
            Dictionary with all key metrics
        """
        # Get date ranges
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Get today's stats
        today_orders = await self._count_orders_in_period(today, today + timedelta(days=1))
        today_revenue = await self._sum_revenue_in_period(today, today + timedelta(days=1))

        # Get yesterday's stats for comparison
        yesterday_orders = await self._count_orders_in_period(yesterday, today)
        yesterday_revenue = await self._sum_revenue_in_period(yesterday, today)

        # Get totals
        total_orders = await self._count_total_orders()
        total_revenue = await self._sum_total_revenue()
        total_customers = await self._count_total_users()
        active_products = await self._count_active_products()

        # Get low stock count
        low_stock_count = await self._count_low_stock_items()

        # Calculate growth
        order_growth = self._calculate_growth(today_orders, yesterday_orders)
        revenue_growth = self._calculate_growth(today_revenue, yesterday_revenue)

        # Get recent orders
        recent_orders = await self.order_repo.get_multi(skip=0, limit=5, filters={})

        # Get top products
        top_products = await self._get_top_selling_products(limit=5)

        return {
            "summary": {
                "today": {
                    "orders": today_orders,
                    "revenue": float(today_revenue) if today_revenue else 0.0,
                    "order_growth": order_growth,
                    "revenue_growth": revenue_growth,
                },
                "totals": {
                    "orders": total_orders,
                    "revenue": float(total_revenue) if total_revenue else 0.0,
                    "customers": total_customers,
                    "active_products": active_products,
                },
                "alerts": {
                    "low_stock_items": low_stock_count,
                    "pending_orders": await self._count_orders_by_status(OrderStatus.PENDING),
                }
            },
            "recent_orders": [self._format_order(order) for order in recent_orders],
            "top_products": top_products,
        }

    async def get_sales_metrics(self, period: str) -> Dict[str, Any]:
        """
        Get sales metrics for specified period.

        Args:
            period: Time period (24h, 7d, 30d, 90d, 1y)

        Returns:
            Sales metrics dictionary
        """
        days = self._parse_period(period)
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()

        # Get metrics
        total_orders = await self._count_orders_in_period(start_date, end_date)
        total_revenue = await self._sum_revenue_in_period(start_date, end_date)
        avg_order_value = float(total_revenue / total_orders) if total_orders > 0 else 0.0

        # Get daily breakdown
        daily_data = await self._get_daily_sales(start_date, end_date)

        # Calculate growth (compare with previous period)
        prev_start = start_date - timedelta(days=days)
        prev_orders = await self._count_orders_in_period(prev_start, start_date)
        prev_revenue = await self._sum_revenue_in_period(prev_start, start_date)

        order_growth = self._calculate_growth(total_orders, prev_orders)
        revenue_growth = self._calculate_growth(float(total_revenue) if total_revenue else 0,
                                                float(prev_revenue) if prev_revenue else 0)

        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "metrics": {
                "total_orders": total_orders,
                "total_revenue": float(total_revenue) if total_revenue else 0.0,
                "average_order_value": avg_order_value,
                "order_growth_percentage": order_growth,
                "revenue_growth_percentage": revenue_growth,
            },
            "daily_breakdown": daily_data,
        }

    async def get_revenue_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get revenue metrics with breakdown."""
        total_revenue = await self._sum_revenue_in_period(start_date, end_date)

        # Revenue by payment method
        revenue_by_payment = await self._get_revenue_by_payment_method(start_date, end_date)

        # Revenue by order type
        revenue_by_type = await self._get_revenue_by_order_type(start_date, end_date)

        # Daily revenue
        daily_revenue = await self._get_daily_revenue(start_date, end_date)

        return {
            "total_revenue": float(total_revenue) if total_revenue else 0.0,
            "revenue_by_payment_method": revenue_by_payment,
            "revenue_by_order_type": revenue_by_type,
            "daily_revenue": daily_revenue,
        }

    async def get_product_metrics(self) -> Dict[str, Any]:
        """Get product metrics and insights."""
        total_products = await self._count_total_products()
        active_products = await self._count_active_products()
        low_stock = await self._get_low_stock_products(limit=10)
        out_of_stock = await self._get_out_of_stock_products(limit=10)
        top_selling = await self._get_top_selling_products(limit=10)

        return {
            "total_products": total_products,
            "active_products": active_products,
            "inactive_products": total_products - active_products,
            "low_stock_count": len(low_stock),
            "out_of_stock_count": len(out_of_stock),
            "low_stock_products": low_stock,
            "out_of_stock_products": out_of_stock,
            "top_selling_products": top_selling,
        }

    async def get_customer_metrics(self, period: str) -> Dict[str, Any]:
        """Get customer metrics."""
        days = self._parse_period(period)
        start_date = datetime.utcnow() - timedelta(days=days)

        total_customers = await self._count_total_users()
        new_customers = await self._count_users_since(start_date)

        # Get top customers by spending
        top_customers = await self._get_top_customers(limit=10)

        # Calculate growth
        prev_start = start_date - timedelta(days=days)
        prev_customers = await self._count_users_since(prev_start)
        prev_new = prev_customers - (total_customers - new_customers)
        growth = self._calculate_growth(new_customers, prev_new)

        return {
            "total_customers": total_customers,
            "new_customers_in_period": new_customers,
            "customer_growth_percentage": growth,
            "top_customers": top_customers,
        }

    async def get_order_metrics(self, period: str) -> Dict[str, Any]:
        """Get order metrics and status distribution."""
        days = self._parse_period(period)
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()

        total_orders = await self._count_orders_in_period(start_date, end_date)

        # Orders by status
        orders_by_status = {}
        for status in OrderStatus:
            count = await self._count_orders_by_status(status, start_date, end_date)
            orders_by_status[status.value] = count

        return {
            "period": period,
            "total_orders": total_orders,
            "orders_by_status": orders_by_status,
            "pending_orders": orders_by_status.get(OrderStatus.PENDING.value, 0),
            "completed_orders": orders_by_status.get(OrderStatus.DELIVERED.value, 0),
            "cancelled_orders": orders_by_status.get(OrderStatus.CANCELLED.value, 0),
        }

    async def get_inventory_metrics(self) -> Dict[str, Any]:
        """Get inventory health metrics."""
        low_stock = await self._get_low_stock_products(limit=100)
        out_of_stock = await self._get_out_of_stock_products(limit=100)

        # Calculate total stock value
        total_value = await self._calculate_total_stock_value()

        return {
            "total_stock_value": float(total_value) if total_value else 0.0,
            "low_stock_count": len(low_stock),
            "out_of_stock_count": len(out_of_stock),
            "low_stock_items": low_stock[:10],  # Top 10
            "out_of_stock_items": out_of_stock[:10],  # Top 10
        }

    async def get_recent_activity(self, limit: int) -> Dict[str, Any]:
        """Get recent activity feed."""
        recent_orders = await self.order_repo.get_multi(skip=0, limit=limit, filters={})
        recent_users = await self._get_recent_users(limit)

        return {
            "recent_orders": [self._format_order(order) for order in recent_orders],
            "recent_customers": [self._format_user(user) for user in recent_users],
        }

    async def get_performance_kpis(self) -> Dict[str, Any]:
        """Get key performance indicators."""
        # Calculate KPIs for last 30 days
        days = 30
        start_date = datetime.utcnow() - timedelta(days=days)

        total_orders = await self._count_orders_in_period(start_date, datetime.utcnow())
        total_revenue = await self._sum_revenue_in_period(start_date, datetime.utcnow())
        avg_order_value = float(total_revenue / total_orders) if total_orders > 0 else 0.0

        return {
            "period_days": days,
            "average_order_value": avg_order_value,
            "total_orders": total_orders,
            "total_revenue": float(total_revenue) if total_revenue else 0.0,
        }

    async def get_top_products(self, period: str, limit: int) -> List[Dict]:
        """Get top selling products."""
        return await self._get_top_selling_products(limit)

    async def get_dashboard_alerts(self) -> Dict[str, Any]:
        """Get dashboard alerts."""
        low_stock_count = await self._count_low_stock_items()
        out_of_stock_count = await self._count_out_of_stock_items()
        pending_orders = await self._count_orders_by_status(OrderStatus.PENDING)

        return {
            "low_stock_alert": {
                "count": low_stock_count,
                "severity": "warning" if low_stock_count > 0 else "info",
            },
            "out_of_stock_alert": {
                "count": out_of_stock_count,
                "severity": "critical" if out_of_stock_count > 0 else "info",
            },
            "pending_orders_alert": {
                "count": pending_orders,
                "severity": "info",
            },
        }

    # Helper methods
    def _parse_period(self, period: str) -> int:
        """Parse period string to days."""
        mapping = {
            "24h": 1,
            "7d": 7,
            "30d": 30,
            "90d": 90,
            "1y": 365,
        }
        return mapping.get(period, 7)

    def _calculate_growth(self, current: float, previous: float) -> float:
        """Calculate growth percentage."""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 2)

    def _format_order(self, order: Order) -> Dict:
        """Format order for response."""
        return {
            "id": str(order.id),
            "order_number": order.order_number,
            "total_amount": float(order.total_amount),
            "status": order.status.value,
            "payment_status": order.payment_status.value,
            "created_at": order.created_at.isoformat(),
        }

    def _format_user(self, user: User) -> Dict:
        """Format user for response."""
        return {
            "id": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "created_at": user.created_at.isoformat(),
        }

    # Database query helpers
    async def _count_orders_in_period(self, start: datetime, end: datetime) -> int:
        """Count orders in date range."""
        db = self.order_repo.db
        query = select(func.count(Order.id)).where(
            and_(
                Order.created_at >= start,
                Order.created_at < end
            )
        )
        result = await db.execute(query)
        return result.scalar() or 0

    async def _sum_revenue_in_period(self, start: datetime, end: datetime) -> float:
        """Sum revenue in date range."""
        db = self.order_repo.db
        query = select(func.sum(Order.total_amount)).where(
            and_(
                Order.created_at >= start,
                Order.created_at < end,
                Order.payment_status == PaymentStatus.COMPLETED
            )
        )
        result = await db.execute(query)
        return result.scalar() or 0.0

    async def _count_total_orders(self) -> int:
        """Count total orders."""
        db = self.order_repo.db
        query = select(func.count(Order.id))
        result = await db.execute(query)
        return result.scalar() or 0

    async def _sum_total_revenue(self) -> float:
        """Sum total revenue."""
        db = self.order_repo.db
        query = select(func.sum(Order.total_amount)).where(
            Order.payment_status == PaymentStatus.COMPLETED
        )
        result = await db.execute(query)
        return result.scalar() or 0.0

    async def _count_total_users(self) -> int:
        """Count total users."""
        db = self.user_repo.db
        query = select(func.count(User.id))
        result = await db.execute(query)
        return result.scalar() or 0

    async def _count_users_since(self, since: datetime) -> int:
        """Count users created since date."""
        db = self.user_repo.db
        query = select(func.count(User.id)).where(User.created_at >= since)
        result = await db.execute(query)
        return result.scalar() or 0

    async def _count_active_products(self) -> int:
        """Count active products."""
        db = self.product_repo.db
        query = select(func.count(Product.id)).where(Product.is_active == True)
        result = await db.execute(query)
        return result.scalar() or 0

    async def _count_total_products(self) -> int:
        """Count total products."""
        db = self.product_repo.db
        query = select(func.count(Product.id))
        result = await db.execute(query)
        return result.scalar() or 0

    async def _count_low_stock_items(self) -> int:
        """Count low stock items."""
        db = self.inventory_repo.db
        query = select(func.count(Inventory.id)).where(
            and_(
                Inventory.stock_quantity > 0,
                Inventory.stock_quantity <= Inventory.low_stock_threshold
            )
        )
        result = await db.execute(query)
        return result.scalar() or 0

    async def _count_out_of_stock_items(self) -> int:
        """Count out of stock items."""
        db = self.inventory_repo.db
        query = select(func.count(Inventory.id)).where(Inventory.stock_quantity == 0)
        result = await db.execute(query)
        return result.scalar() or 0

    async def _count_orders_by_status(
        self,
        status: OrderStatus,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> int:
        """Count orders by status."""
        db = self.order_repo.db
        conditions = [Order.status == status]

        if start_date:
            conditions.append(Order.created_at >= start_date)
        if end_date:
            conditions.append(Order.created_at < end_date)

        query = select(func.count(Order.id)).where(and_(*conditions))
        result = await db.execute(query)
        return result.scalar() or 0

    async def _get_daily_sales(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get daily sales breakdown."""
        # Simplified version - returns empty list for now
        # TODO: Implement proper daily aggregation
        return []

    async def _get_daily_revenue(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get daily revenue breakdown."""
        # Simplified version - returns empty list for now
        # TODO: Implement proper daily aggregation
        return []

    async def _get_revenue_by_payment_method(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """Get revenue breakdown by payment method."""
        # Simplified version
        return {}

    async def _get_revenue_by_order_type(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """Get revenue breakdown by order type."""
        # Simplified version
        return {}

    async def _get_top_selling_products(self, limit: int) -> List[Dict]:
        """Get top selling products."""
        # Simplified version
        return []

    async def _get_low_stock_products(self, limit: int) -> List[Dict]:
        """Get low stock products."""
        # Simplified version
        return []

    async def _get_out_of_stock_products(self, limit: int) -> List[Dict]:
        """Get out of stock products."""
        # Simplified version
        return []

    async def _get_top_customers(self, limit: int) -> List[Dict]:
        """Get top customers by spending."""
        # Simplified version
        return []

    async def _get_recent_users(self, limit: int) -> List[User]:
        """Get recently registered users."""
        db = self.user_repo.db
        query = select(User).order_by(desc(User.created_at)).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def _calculate_total_stock_value(self) -> float:
        """Calculate total value of stock."""
        # Simplified version
        return 0.0
