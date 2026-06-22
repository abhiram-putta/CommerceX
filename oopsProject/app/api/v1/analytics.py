"""
Analytics endpoints for sales reports and insights.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, require_seller
from app.config.database import get_db
from app.models.order import Order
from app.models.payment import Payment
from app.models.product import Product
from app.models.review import Review
from app.models.user import User
from app.utils.enums import OrderStatus, PaymentStatus

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(
    current_user: User = Depends(require_seller),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get dashboard statistics for sellers.

    Returns:
    - Total sales
    - Total orders
    - Total revenue
    - Average order value
    - Recent orders count (last 7 days)
    """
    # Total orders for this seller
    total_orders_query = select(func.count(Order.id)).where(
        Order.retailer_id == current_user.id
    )
    total_orders_result = await db.execute(total_orders_query)
    total_orders = total_orders_result.scalar() or 0

    # Total revenue (successful payments)
    total_revenue_query = select(func.sum(Payment.amount)).where(
        Payment.user_id == current_user.id,
        Payment.status == PaymentStatus.SUCCESS
    )
    total_revenue_result = await db.execute(total_revenue_query)
    total_revenue = total_revenue_result.scalar() or 0.0

    # Average order value
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0

    # Recent orders (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_orders_query = select(func.count(Order.id)).where(
        Order.retailer_id == current_user.id,
        Order.created_at >= seven_days_ago
    )
    recent_orders_result = await db.execute(recent_orders_query)
    recent_orders = recent_orders_result.scalar() or 0

    # Pending orders
    pending_orders_query = select(func.count(Order.id)).where(
        Order.retailer_id == current_user.id,
        Order.status == OrderStatus.PENDING
    )
    pending_orders_result = await db.execute(pending_orders_query)
    pending_orders = pending_orders_result.scalar() or 0

    return {
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "average_order_value": float(avg_order_value),
        "recent_orders_7d": recent_orders,
        "pending_orders": pending_orders,
        "currency": "INR"
    }


@router.get("/sales-report")
async def get_sales_report(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    current_user: User = Depends(require_seller),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get sales report for a date range.

    - **start_date**: Start date (optional, defaults to 30 days ago)
    - **end_date**: End date (optional, defaults to now)

    Returns:
    - Total sales
    - Total orders
    - Revenue breakdown by status
    - Average order value
    """
    # Default to last 30 days if not specified
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()

    # Orders in date range
    orders_query = select(Order).where(
        Order.retailer_id == current_user.id,
        Order.created_at >= start_date,
        Order.created_at <= end_date
    )
    orders_result = await db.execute(orders_query)
    orders = orders_result.scalars().all()

    # Calculate metrics
    total_orders = len(orders)
    total_revenue = sum(order.total_amount for order in orders)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0

    # Revenue by status
    revenue_by_status = {}
    for status in OrderStatus:
        status_orders = [o for o in orders if o.status == status]
        revenue_by_status[status.value] = sum(o.total_amount for o in status_orders)

    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "average_order_value": float(avg_order_value),
        "revenue_by_status": {k: float(v) for k, v in revenue_by_status.items()},
        "currency": "INR"
    }


@router.get("/product-performance")
async def get_product_performance(
    limit: int = Query(10, ge=1, le=50, description="Top N products"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get top performing products.

    - **limit**: Number of top products to return

    Returns top products by:
    - Sales count
    - Revenue
    - Average rating
    """
    # This is a simplified version
    # For sellers, you'd filter by their inventory

    # Top products by review ratings
    top_rated_query = (
        select(
            Product.id,
            Product.name,
            func.avg(Review.rating).label('avg_rating'),
            func.count(Review.id).label('review_count')
        )
        .join(Review, Review.product_id == Product.id)
        .group_by(Product.id, Product.name)
        .order_by(func.avg(Review.rating).desc())
        .limit(limit)
    )

    top_rated_result = await db.execute(top_rated_query)
    top_rated = top_rated_result.all()

    top_products = [
        {
            "product_id": str(row.id),
            "product_name": row.name,
            "average_rating": float(row.avg_rating) if row.avg_rating else 0.0,
            "review_count": row.review_count
        }
        for row in top_rated
    ]

    return {
        "top_products": top_products,
        "metric": "rating"
    }


@router.get("/revenue-chart")
async def get_revenue_chart(
    days: int = Query(30, ge=7, le=365, description="Number of days"),
    current_user: User = Depends(require_seller),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get revenue chart data for the last N days.

    - **days**: Number of days to include (7-365)

    Returns daily revenue data for charting.
    """
    start_date = datetime.utcnow() - timedelta(days=days)

    # Get orders in range
    orders_query = select(Order).where(
        Order.retailer_id == current_user.id,
        Order.created_at >= start_date,
        Order.status != OrderStatus.CANCELLED
    )
    orders_result = await db.execute(orders_query)
    orders = orders_result.scalars().all()

    # Group by date
    revenue_by_date = {}
    for order in orders:
        date_key = order.created_at.date().isoformat()
        if date_key not in revenue_by_date:
            revenue_by_date[date_key] = 0.0
        revenue_by_date[date_key] += order.total_amount

    # Create time series (fill missing dates with 0)
    chart_data = []
    current_date = start_date.date()
    end_date = datetime.utcnow().date()

    while current_date <= end_date:
        date_str = current_date.isoformat()
        chart_data.append({
            "date": date_str,
            "revenue": float(revenue_by_date.get(date_str, 0.0))
        })
        current_date += timedelta(days=1)

    return {
        "period_days": days,
        "data": chart_data,
        "currency": "INR"
    }
