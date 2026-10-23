from datetime import datetime
from decimal import Decimal

import pytest

from app.services.order_service import calculate_order_total
from app.services.delivery_service import (
    get_offer_expiry,
    is_offer_expired,
)




def test_calculate_order_total():
    total = calculate_order_total(
        subtotal=Decimal("200.00"),
        discount_amount=Decimal("20.00"),
        packaging_fee=Decimal("5.00"),
        delivery_fee=Decimal("10.00"),
        platform_fee=Decimal("3.00"),
    )

    assert total == Decimal("198.00")


def test_calculate_order_total_without_fees():
    total = calculate_order_total(
        subtotal=Decimal("100.00"),
    )

    assert total == Decimal("100.00")


def test_discount_cannot_exceed_subtotal():
    with pytest.raises(ValueError):
        calculate_order_total(
            subtotal=Decimal("100.00"),
            discount_amount=Decimal("150.00"),
        )


def test_negative_subtotal_is_rejected():
    with pytest.raises(ValueError):
        calculate_order_total(
            subtotal=Decimal("-10.00"),
        )


def test_negative_fee_is_rejected():
    with pytest.raises(ValueError):
        calculate_order_total(
            subtotal=Decimal("100.00"),
            delivery_fee=Decimal("-5.00"),
        )


def test_float_subtotal_is_rejected():
    with pytest.raises(TypeError):
        calculate_order_total(
            subtotal=100.00,
        )


# -----------------------------
# Delivery Service Tests
# -----------------------------

def test_offer_expiry_is_in_future():
    before = datetime.now()
    expiry = get_offer_expiry(minutes=10)
    after = datetime.now()

    assert expiry > before
    assert expiry > after
    assert not is_offer_expired(expiry)


def test_offer_is_expired():
    expiry = datetime(2000, 1, 1)

    assert is_offer_expired(expiry)


def test_invalid_offer_expiry():
    with pytest.raises(ValueError):
        get_offer_expiry(minutes=0)


def test_negative_offer_expiry():
    with pytest.raises(ValueError):
        get_offer_expiry(minutes=-5)