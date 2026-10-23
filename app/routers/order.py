from decimal import Decimal
from uuid import uuid4
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.user import User
from app.models.order import Order, OrderStatus, PaymentMethod, PaymentStatus
from app.models.order_item import OrderItem
from app.models.order_status_history import OrderStatusHistory
from app.models.cart import Cart
from app.models.address import Address
from app.models.menu_item import MenuItem
from app.routers.auth import get_current_user
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.value != "Customer":
        raise HTTPException(status_code=403, detail="Only customers can place orders")

    address = db.query(Address).filter(
        Address.id == order_data.address_id,
        Address.user_id == current_user.id,
    ).first()

    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    cart = (
        db.query(Cart)
        .options(joinedload(Cart.items))
        .filter(Cart.customer_id == current_user.id)
        .first()
    )

    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Your cart is empty")

    restaurant_id = cart.restaurant_id
    if restaurant_id is None:
        raise HTTPException(status_code=400, detail="Your cart has no restaurant")

    item_total = Decimal("0.00")
    order_items = []

    for cart_item in cart.items:
        menu_item = db.query(MenuItem).filter(
            MenuItem.id == cart_item.menu_item_id,
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.is_available.is_(True),
            MenuItem.is_deleted.is_(False),
        ).first()

        if not menu_item:
            raise HTTPException(
                status_code=400,
                detail=f"Menu item {cart_item.menu_item_id} is unavailable",
            )

        unit_price = Decimal(str(menu_item.price))
        quantity = cart_item.quantity
        item_total += unit_price * quantity

        order_items.append(
            OrderItem(
                menu_item_id=menu_item.id,
                item_name=menu_item.name,
                unit_price=unit_price,
                quantity=quantity,
            )
        )

    packaging_fee = Decimal("10.00")
    delivery_fee = Decimal("30.00")
    platform_fee = Decimal("5.00")
    discount_amount = Decimal("0.00")
    tip_amount = Decimal(str(order_data.tip))
    gst_amount = (item_total * Decimal("0.05")).quantize(Decimal("0.01"))
    grand_total = (
        item_total + packaging_fee + delivery_fee
        + platform_fee + gst_amount + tip_amount - discount_amount
    )

    order = Order(
        order_number=f"FD-{uuid4().hex[:10].upper()}",
        customer_id=current_user.id,
        restaurant_id=restaurant_id,
        address_id=address.id,
        status=OrderStatus.PLACED,
        payment_method=order_data.payment_method,
        payment_status=PaymentStatus.PENDING,
        item_total=item_total,
        discount_amount=discount_amount,
        packaging_fee=packaging_fee,
        delivery_fee=delivery_fee,
        platform_fee=platform_fee,
        gst_amount=gst_amount,
        tip_amount=tip_amount,
        grand_total=grand_total,
        delivery_otp=f"{secrets.randbelow(10000):04d}",
    )

    try:
        db.add(order)
        db.flush()

        for item in order_items:
            item.order_id = order.id
            db.add(item)

        history = OrderStatusHistory(
            order_id=order.id,
            status=OrderStatus.PLACED,
            changed_by_id=current_user.id,
            changed_by_role="Customer",
            note="Order placed",
        )
        db.add(history)

        for cart_item in list(cart.items):
            db.delete(cart_item)

        cart.restaurant_id = None
        db.commit()

        saved_order = (
            db.query(Order)
            .options(joinedload(Order.items))
            .filter(Order.id == order.id)
            .first()
        )
        return saved_order

    except Exception:
        db.rollback()
        raise


@router.get("/", response_model=list[OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.customer_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    is_customer = (
        current_user.role.value == "Customer"
        and order.customer_id == current_user.id
    )
    is_admin = current_user.role.value == "Admin"

    if not (is_customer or is_admin):
        raise HTTPException(status_code=403, detail="You cannot view this order")

    return order