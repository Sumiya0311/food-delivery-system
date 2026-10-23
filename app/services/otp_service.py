import secrets
from datetime import datetime, timedelta


def generate_otp() -> str:
    """Generate a secure 6-digit OTP."""
    return f"{secrets.randbelow(900000) + 100000:06d}"


def get_otp_expiry(minutes: int = 5) -> datetime:
    """Return the OTP expiry time."""
    if minutes <= 0:
        raise ValueError("OTP expiry must be greater than zero minutes")

    return datetime.now() + timedelta(minutes=minutes)


def is_otp_expired(expires_at: datetime) -> bool:
    """Check whether the OTP has expired."""
    now = datetime.now()

    if expires_at.tzinfo is not None and now.tzinfo is None:
        now = now.replace(tzinfo=expires_at.tzinfo)
    elif expires_at.tzinfo is None and now.tzinfo is not None:
        expires_at = expires_at.replace(tzinfo=now.tzinfo)

    return expires_at <= now