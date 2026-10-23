from datetime import datetime, timedelta


def get_offer_expiry(minutes: int = 10) -> datetime:
    """Return the expiry time for a delivery offer."""
    if minutes <= 0:
        raise ValueError("Offer expiry must be greater than zero minutes")

    return datetime.now() + timedelta(minutes=minutes)


def is_offer_expired(expires_at: datetime) -> bool:
    """Check whether a delivery offer has expired."""
    now = datetime.now()

    
    if expires_at.tzinfo is not None and now.tzinfo is None:
        now = now.replace(tzinfo=expires_at.tzinfo)
    elif expires_at.tzinfo is None and now.tzinfo is not None:
        expires_at = expires_at.replace(tzinfo=now.tzinfo)

    return expires_at <= now