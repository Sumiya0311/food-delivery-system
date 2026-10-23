import re


def validate_phone_number(phone: str) -> bool:
    """Validate a 10-digit Indian mobile number."""
    return bool(re.fullmatch(r"[6-9]\d{9}", phone))


def validate_email(email: str) -> bool:
    """Basic email format validation."""
    pattern = r"^[\w.+-]+@[\w-]+(?:\.[\w-]+)+$"
    return bool(re.fullmatch(pattern, email))


def validate_password(password: str) -> bool:
    """Require at least 8 characters."""
    return len(password) >= 8