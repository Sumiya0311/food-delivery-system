from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.order import Order, OrderStatus
from app.models.order_status_history import OrderStatusHistory
from app.models.delivery_partner import DeliveryPartner
from app.models.delivery_offer import DeliveryOffer
from app.models.notification import Notification
from app.routers.auth import get_current_user
from app.schemas.order import OrderResponse


router = APIRouter(
    prefix="/restaurant-orders",
    tags=["Restaurant Orders"],
)


def check_restaurant_owner(current_user: User):
    if current_user.role.value != "Restaurant Owner":
        raise HTTPException(
            status_code=403,
            detail="Only restaurant owners can perform this action",
        )


def get_owned_restaurant(
    db: Session,
    user_id: int,
) -> Restaurant:
    restaurant = (
        db.query(Restaurant)
        .filter(
            Restaurant.owner_id == user_id,
            Restaurant.is_active.is_(True),
        )
        .first()
    )

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="No active restaurant found for this owner",
        )

    return restaurant


def get_owned_order(
    db: Session,
    order_id: int,
    restaurant_id: int,
) -> Order:
    order = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(
            Order.id == order_id,
            Order.restaurant_id == restaurant_id,
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return order


def add_order_history(
    db: Session,
    order: Order,
    user: User,
    status: OrderStatus,
    note: str,
):
    db.add(
        OrderStatusHistory(
            order_id=order.id,
            status=status.value,
            changed_by_id=user.id,
            changed_by_role="Restaurant Owner",
            note=note,
        )
    )


def add_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: str = "order_status",
):
    db.add(
        Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            is_read=False,
        )
    )
    db.commit()



@router.get("/", response_model=list[OrderResponse])
def get_restaurant_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_restaurant_owner(current_user)

    restaurant = get_owned_restaurant(db, current_user.id)

    return (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.restaurant_id == restaurant.id)
        .order_by(Order.created_at.desc())
        .all()
    )


@router.patch("/{order_id}/accept", response_model=OrderResponse)
def accept_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_restaurant_owner(current_user)

    restaurant = get_owned_restaurant(db, current_user.id)
    order = get_owned_order(db, order_id, restaurant.id)

    if order.status != OrderStatus.PLACED:
        raise HTTPException(
            status_code=400,
            detail="Only placed orders can be accepted",
        )

    try:
        order.status = OrderStatus.ACCEPTED

        add_order_history(
            db,
            order,
            current_user,
            OrderStatus.ACCEPTED,
            "Order accepted by restaurant",
        )

        add_notification(
            db,
            order.customer_id,
            "Order Accepted",
            f"Your order #{order.id} has been accepted by the restaurant.",
        )

        db.commit()
        db.refresh(order)
        return order

    except Exception:
        db.rollback()
        raise


@router.patch("/{order_id}/reject", response_model=OrderResponse)
def reject_order(
    order_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_restaurant_owner(current_user)

    restaurant = get_owned_restaurant(db, current_user.id)
    order = get_owned_order(db, order_id, restaurant.id)

    if order.status != OrderStatus.PLACED:
        raise HTTPException(
            status_code=400,
            detail="Only placed orders can be rejected",
        )

    reason = reason.strip()

    if not reason:
        raise HTTPException(
            status_code=422,
            detail="Rejection reason cannot be empty",
        )

    try:
        order.status = OrderStatus.REJECTED
        order.rejection_reason = reason

        add_order_history(
            db,
            order,
            current_user,
            OrderStatus.REJECTED,
            reason,
        )

        add_notification(
            db,
            order.customer_id,
            "Order Rejected",
            f"Your order #{order.id} was rejected. Reason: {reason}",
        )

        db.commit()
        db.refresh(order)
        return order

    except Exception:
        db.rollback()
        raise


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    new_status: OrderStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_restaurant_owner(current_user)

    restaurant = get_owned_restaurant(db, current_user.id)
    order = get_owned_order(db, order_id, restaurant.id)

    allowed_transitions = {
        OrderStatus.ACCEPTED: [OrderStatus.PREPARING],
        OrderStatus.PREPARING: [OrderStatus.READY],
    }

    if new_status not in allowed_transitions.get(order.status, []):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot change status from {order.status.value} "
                f"to {new_status.value}"
            ),
        )

    try:
        order.status = new_status

        add_order_history(
            db,
            order,
            current_user,
            new_status,
            f"Order status changed to {new_status.value}",
        )

        add_notification(
            db,
            order.customer_id,
            f"Order {new_status.value}",
            f"Your order #{order.id} status is now {new_status.value}.",
        )

        # When an order becomes Ready, create offers for available partners.
        if new_status == OrderStatus.READY:
            now = datetime.now()

            # Expire old Pending offers for this order.
            db.query(DeliveryOffer).filter(
                DeliveryOffer.order_id == order.id,
                DeliveryOffer.status == "Pending",
                DeliveryOffer.expires_at <= now,
            ).update(
                {"status": "Expired"},
                synchronize_session=False,
            )

            partners = (
                db.query(DeliveryPartner)
                .filter(
                    DeliveryPartner.is_online.is_(True),
                    DeliveryPartner.is_available.is_(True),
                )
                .all()
            )

            print("Order ready:", order.id)
            print("Available delivery partners:", len(partners))

            for partner in partners:
                existing_offer = (
                    db.query(DeliveryOffer)
                    .filter(
                        DeliveryOffer.order_id == order.id,
                        DeliveryOffer.partner_id == partner.id,
                        DeliveryOffer.status.in_(["Pending", "Accepted"]),
                    )
                    .first()
                )

                if existing_offer:
                    continue

                db.add(
                    DeliveryOffer(
                        order_id=order.id,
                        partner_id=partner.id,
                        status="Pending",
                        offered_at=now,
                        expires_at=now + timedelta(minutes=10),
                    )
                )

        db.commit()
        db.refresh(order)
        return order

    except Exception:
        db.rollback()
        raise


@router.post("/{order_id}/create-delivery-offers")
def create_delivery_offers(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_restaurant_owner(current_user)

    restaurant = get_owned_restaurant(db, current_user.id)
    order = get_owned_order(db, order_id, restaurant.id)

    if order.status != OrderStatus.READY:
        raise HTTPException(
            status_code=400,
            detail="Only Ready orders can receive delivery offers",
        )

    now = datetime.now()

    try:
        db.query(DeliveryOffer).filter(
            DeliveryOffer.order_id == order.id,
            DeliveryOffer.status == "Pending",
            DeliveryOffer.expires_at <= now,
        ).update(
            {"status": "Expired"},
            synchronize_session=False,
        )

        partners = (
            db.query(DeliveryPartner)
            .filter(
                DeliveryPartner.is_online.is_(True),
                DeliveryPartner.is_available.is_(True),
            )
            .all()
        )

        print("Order:", order.id)
        print("Available delivery partners:", len(partners))

        created_partner_ids = []

        for partner in partners:
            existing_offer = (
                db.query(DeliveryOffer)
                .filter(
                    DeliveryOffer.order_id == order.id,
                    DeliveryOffer.partner_id == partner.id,
                    DeliveryOffer.status.in_(["Pending", "Accepted"]),
                )
                .first()
            )

            if existing_offer:
                continue

            db.add(
                DeliveryOffer(
                    order_id=order.id,
                    partner_id=partner.id,
                    status="Pending",
                    offered_at=now,
                    expires_at=now + timedelta(minutes=10),
                )
            )

            created_partner_ids.append(partner.id)

        if not created_partner_ids:
            db.commit()

            raise HTTPException(
                status_code=409,
                detail=(
                    "No new offers created. Check that a delivery partner "
                    "is online and available, and that no active offer "
                    "already exists for this order."
                ),
            )

        db.commit()

        print("Delivery offers created:", len(created_partner_ids))

        return {
            "message": "Delivery offers created successfully",
            "order_id": order.id,
            "partner_ids": created_partner_ids,
            "offers_created": len(created_partner_ids),
        }

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise