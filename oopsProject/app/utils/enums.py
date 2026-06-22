"""
Enumerations used across the application.
"""
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""
    CUSTOMER = "customer"
    RETAILER = "retailer"
    WHOLESALER = "wholesaler"
    ADMIN = "admin"


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    PACKED = "packed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    """Payment method enumeration."""
    ONLINE = "online"
    COD = "cod"
    CREDIT = "credit"


class OrderType(str, Enum):
    """Order type enumeration."""
    ONLINE = "online"
    OFFLINE = "offline"


class OwnerType(str, Enum):
    """Inventory owner type enumeration."""
    RETAILER = "retailer"
    WHOLESALER = "wholesaler"


class InteractionType(str, Enum):
    """User interaction type for ML tracking."""
    VIEW = "view"
    ADD_TO_CART = "add_to_cart"
    REMOVE_FROM_CART = "remove_from_cart"
    PURCHASE = "purchase"
    WISHLIST = "wishlist"
    SEARCH = "search"


class NotificationType(str, Enum):
    """Notification type enumeration."""
    ORDER_UPDATE = "order_update"
    PROMOTION = "promotion"
    STOCK_ALERT = "stock_alert"
    PAYMENT = "payment"
    REVIEW = "review"
    GENERAL = "general"


class StockAlertType(str, Enum):
    """Stock alert type enumeration."""
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    RESTOCK_NEEDED = "restock_needed"


class Gender(str, Enum):
    """Gender enumeration."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class CouponType(str, Enum):
    """Coupon type enumeration."""
    GENERAL = "general"
    FIRST_TIME_USER = "first_time_user"
    PRODUCT_SPECIFIC = "product_specific"
    CATEGORY_SPECIFIC = "category_specific"
    USER_SPECIFIC = "user_specific"


class DiscountType(str, Enum):
    """Discount type enumeration."""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"


class ReturnReason(str, Enum):
    """Return reason enumeration."""
    DEFECTIVE = "defective"
    WRONG_ITEM = "wrong_item"
    NOT_AS_DESCRIBED = "not_as_described"
    SIZE_ISSUE = "size_issue"
    QUALITY_ISSUE = "quality_issue"
    CHANGED_MIND = "changed_mind"
    DAMAGED_SHIPPING = "damaged_shipping"
    OTHER = "other"


class ReturnStatus(str, Enum):
    """Return status enumeration."""
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    PICKUP_SCHEDULED = "pickup_scheduled"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    RECEIVED = "received"
    INSPECTED = "inspected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RefundStatus(str, Enum):
    """Refund status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
