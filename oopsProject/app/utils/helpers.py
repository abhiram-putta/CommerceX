"""
Helper utility functions.
"""
import secrets
import string
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from uuid import UUID

import pytz


def generate_random_string(length: int = 32) -> str:
    """
    Generate a random alphanumeric string.

    Args:
        length: Length of the string to generate

    Returns:
        Random string
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_otp(length: int = 6) -> str:
    """
    Generate a numeric OTP.

    Args:
        length: Length of the OTP

    Returns:
        Numeric OTP string
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def generate_order_number() -> str:
    """
    Generate a unique order number.

    Returns:
        Order number in format: ORD-YYYYMMDD-XXXXXX
    """
    date_str = datetime.utcnow().strftime("%Y%m%d")
    random_suffix = generate_random_string(6).upper()
    return f"ORD-{date_str}-{random_suffix}"


def is_valid_uuid(value: str) -> bool:
    """
    Check if a string is a valid UUID.

    Args:
        value: String to check

    Returns:
        True if valid UUID, False otherwise
    """
    try:
        UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


def get_utc_now() -> datetime:
    """
    Get current UTC datetime.

    Returns:
        Current UTC datetime
    """
    return datetime.now(pytz.UTC)


def add_days(date: datetime, days: int) -> datetime:
    """
    Add days to a datetime.

    Args:
        date: Base datetime
        days: Number of days to add

    Returns:
        New datetime
    """
    return date + timedelta(days=days)


def add_hours(date: datetime, hours: int) -> datetime:
    """
    Add hours to a datetime.

    Args:
        date: Base datetime
        hours: Number of hours to add

    Returns:
        New datetime
    """
    return date + timedelta(hours=hours)


def add_minutes(date: datetime, minutes: int) -> datetime:
    """
    Add minutes to a datetime.

    Args:
        date: Base datetime
        minutes: Number of minutes to add

    Returns:
        New datetime
    """
    return date + timedelta(minutes=minutes)


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.

    Args:
        text: Text to convert

    Returns:
        Slugified text
    """
    import re
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')


def calculate_percentage(value: float, percentage: float) -> float:
    """
    Calculate percentage of a value.

    Args:
        value: Base value
        percentage: Percentage to calculate

    Returns:
        Calculated percentage amount
    """
    return (value * percentage) / 100.0


def apply_discount(price: float, discount_percentage: float) -> float:
    """
    Apply discount to a price.

    Args:
        price: Original price
        discount_percentage: Discount percentage

    Returns:
        Discounted price
    """
    discount_amount = calculate_percentage(price, discount_percentage)
    return price - discount_amount


def format_currency(amount: float, currency: str = "INR") -> str:
    """
    Format amount as currency string.

    Args:
        amount: Amount to format
        currency: Currency code

    Returns:
        Formatted currency string
    """
    if currency == "INR":
        return f"₹{amount:,.2f}"
    return f"{currency} {amount:,.2f}"


def dict_to_query_params(params: Dict[str, Any]) -> str:
    """
    Convert dictionary to URL query parameters.

    Args:
        params: Dictionary of parameters

    Returns:
        Query parameter string
    """
    from urllib.parse import urlencode
    return urlencode({k: v for k, v in params.items() if v is not None})


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    import re
    # Remove path components
    filename = filename.split('/')[-1].split('\\')[-1]
    # Remove special characters
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    return filename


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.

    Args:
        filename: Filename

    Returns:
        File extension (without dot)
    """
    return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.

    Args:
        lat1: Latitude of point 1
        lon1: Longitude of point 1
        lat2: Latitude of point 2
        lon2: Longitude of point 2

    Returns:
        Distance in kilometers
    """
    from math import radians, sin, cos, sqrt, atan2

    R = 6371.0  # Earth's radius in kilometers

    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


def mask_email(email: str) -> str:
    """
    Mask email address for privacy.

    Args:
        email: Email address

    Returns:
        Masked email (e.g., j***@example.com)
    """
    if '@' not in email:
        return email

    username, domain = email.split('@')
    if len(username) <= 2:
        masked_username = username[0] + '*'
    else:
        masked_username = username[0] + '*' * (len(username) - 2) + username[-1]

    return f"{masked_username}@{domain}"


def mask_phone(phone: str) -> str:
    """
    Mask phone number for privacy.

    Args:
        phone: Phone number

    Returns:
        Masked phone (e.g., +91******1234)
    """
    if len(phone) <= 4:
        return phone

    return phone[:3] + '*' * (len(phone) - 7) + phone[-4:]
