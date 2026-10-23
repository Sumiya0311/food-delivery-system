from decimal import Decimal


def calculate_order_total(
    subtotal: Decimal,
    discount_amount: Decimal = Decimal("0.00"),
    packaging_fee: Decimal = Decimal("0.00"),
    delivery_fee: Decimal = Decimal("0.00"),
    platform_fee: Decimal = Decimal("0.00"),
) -> Decimal:
    """Calculate the final order total after discounts and fees."""

    values = {
        "subtotal": subtotal,
        "discount_amount": discount_amount,
        "packaging_fee": packaging_fee,
        "delivery_fee": delivery_fee,
        "platform_fee": platform_fee,
    }

    for name, value in values.items():
        if not isinstance(value, Decimal):
            raise TypeError(f"{name} must be a Decimal")
        if not value.is_finite():
            raise ValueError(f"{name} must be finite")

    if subtotal < 0:
        raise ValueError("Subtotal cannot be negative")

    for name in ("discount_amount", "packaging_fee",
                 "delivery_fee", "platform_fee"):
        if values[name] < 0:
            raise ValueError(f"{name} cannot be negative")

    if discount_amount > subtotal:
        raise ValueError("Discount cannot exceed subtotal")

    total = (
        subtotal
        - discount_amount
        + packaging_fee
        + delivery_fee
        + platform_fee
    )

    return total.quantize(Decimal("0.01"))