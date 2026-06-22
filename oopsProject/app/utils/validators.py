"""
Custom validators for data validation.
"""
import re
from typing import Any

import phonenumbers
from phonenumbers import NumberParseException


def validate_password_strength(password: str) -> bool:
    """
    Validate password strength.

    Password must:
    - Be at least 8 characters long
    - Contain at least one uppercase letter
    - Contain at least one lowercase letter
    - Contain at least one digit
    - Contain at least one special character

    Args:
        password: Password to validate

    Returns:
        True if password is strong, False otherwise
    """
    if len(password) < 8:
        return False

    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    return has_upper and has_lower and has_digit and has_special


def validate_phone_number(phone: str, region: str = "IN") -> bool:
    """
    Validate phone number using phonenumbers library.

    Args:
        phone: Phone number to validate
        region: Region code (default: IN for India)

    Returns:
        True if valid, False otherwise
    """
    try:
        parsed = phonenumbers.parse(phone, region)
        return phonenumbers.is_valid_number(parsed)
    except NumberParseException:
        return False


def format_phone_number(phone: str, region: str = "IN") -> str:
    """
    Format phone number to international format.

    Args:
        phone: Phone number to format
        region: Region code

    Returns:
        Formatted phone number

    Raises:
        ValueError: If phone number is invalid
    """
    try:
        parsed = phonenumbers.parse(phone, region)
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except NumberParseException as e:
        raise ValueError(f"Invalid phone number: {e}")


def validate_gst_number(gst: str) -> bool:
    """
    Validate Indian GST number.

    Format: 22AAAAA0000A1Z5

    Args:
        gst: GST number to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    return bool(re.match(pattern, gst))


def validate_pincode(pincode: str, country: str = "IN") -> bool:
    """
    Validate postal code/pincode.

    Args:
        pincode: Pincode to validate
        country: Country code

    Returns:
        True if valid, False otherwise
    """
    if country == "IN":
        # Indian pincode: 6 digits
        pattern = r'^\d{6}$'
        return bool(re.match(pattern, pincode))

    # Add more country-specific validations as needed
    return True


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return bool(pattern.match(url))


def validate_rating(rating: int) -> bool:
    """
    Validate rating value.

    Args:
        rating: Rating value (1-5)

    Returns:
        True if valid, False otherwise
    """
    return 1 <= rating <= 5


def sanitize_input(value: str) -> str:
    """
    Sanitize input to prevent XSS attacks.

    Args:
        value: Input string

    Returns:
        Sanitized string
    """
    # Remove HTML tags
    value = re.sub(r'<[^>]*>', '', value)
    # Remove script tags and content
    value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.DOTALL | re.IGNORECASE)
    # Remove javascript: protocol
    value = re.sub(r'javascript:', '', value, flags=re.IGNORECASE)
    return value.strip()


def validate_json_structure(data: Any, required_keys: list) -> bool:
    """
    Validate if dictionary has required keys.

    Args:
        data: Dictionary to validate
        required_keys: List of required keys

    Returns:
        True if all required keys present, False otherwise
    """
    if not isinstance(data, dict):
        return False

    return all(key in data for key in required_keys)
