from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.delivery_partner import DeliveryPartner
from app.models.delivery_offer import DeliveryOffer
from app.models.order import Order, OrderStatus
from app.models.order_status_history import OrderStatusHistory
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.delivery import (
    AvailabilityUpdate,
    DeliveryOfferResponse,
    DeliveryOfferResponseUpdate,
    DeliveryPartnerResponse,
    LocationUpdate,
)
from app.websocket_manager import manager

router = APIRouter(prefix="/delivery", tags=["Delivery"])


# -------------------- HELPERS --------------------

def require_delivery_partner(user: User):
    if user.role.value != "Delivery Partner":
        raise HTTPException(
            status_code=403,
            detail="Only delivery partners can access this endpoint",
        )


def get_partner(db: Session, user_id: int):
    partner = (
        db.query(DeliveryPartner)
        .filter(DeliveryPartner.user_id == user_id)
        .first()
    )

    if not partner:
        raise HTTPException(
            status_code=404,
            detail="Delivery partner profile not found",
        )

    return partner


def get_assigned_order(
    db: Session,
    order_id: int,
    partner_id: int,
):
    assignment = (
        db.query(DeliveryOffer)
        .filter(
            DeliveryOffer.order_id == order_id,
            DeliveryOffer.partner_id == partner_id,
            DeliveryOffer.status == "Accepted",
        )
        .first()
    )

    if not assignment:
        raise HTTPException(
            status_code=403,
            detail="This order is not assigned to you",
        )

    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .with_for_update()
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return order


def record_order_history(
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
            changed_by_role="Delivery Partner",
            note=note,
        )
    )


async def broadcast_order_update(
    order: Order,
    event: str = "order_status",
):
    """Send a real-time update to clients tracking this order."""
    await manager.broadcast(
        order.id,
        {
            "event": "order_status_updated",
            "order_id": order.id,
            "status": order.status.value,
            "message": {
                "Assigned": "Delivery partner assigned",
                "Picked Up": "Order picked up by delivery partner",
                "Out for Delivery": "Order is not for delivery",
                "Delivered": "Order delivered successfully",
            }.get(order.status.value, "Order status updated"),
            "latitude": (
                float(order.delivery_partner.latitude)
                if getattr(order, "delivery_partner", None)
                and order.delivery_partner.latitude is not None
                else None
            ),
            "longitude": (
                float(order.delivery_partner.longitude)
                if getattr(order, "delivery_partner", None)
                and order.delivery_partner.longitude is not None
                else None
            ),
            "updated_at": datetime.utcnow().isoformat(),
        },
    )


# -------------------- LOCATION --------------------

@router.patch("/location", response_model=DeliveryPartnerResponse)
async def update_location(
    data: LocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_delivery_partner(current_user)
    partner = get_partner(db, current_user.id)

    partner.latitude = data.latitude
    partner.longitude = data.longitude

    db.commit()
    db.refresh(partner)

    # Broadcast location to each currently assigned order.
    assignments = (
        db.query(DeliveryOffer)
        .join(Order, Order.id == DeliveryOffer.order_id)
        .filter(
            DeliveryOffer.partner_id == partner.id,
            DeliveryOffer.status == "Accepted",
            Order.status.in_(
                [
                    OrderStatus.ASSIGNED,
                    OrderStatus.PICKED_UP,
                    OrderStatus.OUT_FOR_DELIVERY,
                ]
            ),
        )
        .all()
    )

    for assignment in assignments:
        await manager.broadcast_to_order(
            assignment.order_id,
            {
                "event": "delivery_location",
                "order_id": assignment.order_id,
                "latitude": (
                    float(partner.latitude)
                    if partner.latitude is not None
                    else None
                ),
                "longitude": (
                    float(partner.longitude)
                    if partner.longitude is not None
                    else None
                ),
                "updated_at": datetime.utcnow().isoformat(),
            },
        )

    return partner


# -------------------- AVAILABILITY --------------------

@router.patch("/availability", response_model=DeliveryPartnerResponse)
def update_availability(
    data: AvailabilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_delivery_partner(current_user)
    partner = get_partner(db, current_user.id)

    if not data.is_online:
        partner.is_online = False
        partner.is_available = False
    else:
        partner.is_online = True

        if data.is_available is not None:
            active_assignment = (
                db.query(DeliveryOffer)
                .join(Order, Order.id == DeliveryOffer.order_id)
                .filter(
                    DeliveryOffer.partner_id == partner.id,
                    DeliveryOffer.status == "Accepted",
                    Order.status.in_(
                        [
                            OrderStatus.ASSIGNED,
                            OrderStatus.PICKED_UP,
                            OrderStatus.OUT_FOR_DELIVERY,
                        ]
                    ),
                )
                .first()
            )

            if active_assignment and data.is_available:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "You have an active delivery and cannot "
                        "become available"
                    ),
                )

            partner.is_available = data.is_available

    db.commit()
    db.refresh(partner)
    return partner


# -------------------- PROFILE --------------------

@router.get("/profile", response_model=DeliveryPartnerResponse)
def get_delivery_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_delivery_partner(current_user)
    return get_partner(db, current_user.id)


# -------------------- DELIVERY OFFERS --------------------

@router.get("/offers", response_model=list[DeliveryOfferResponse])
def get_delivery_offers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_delivery_partner(current_user)
    partner = get_partner(db, current_user.id)
    now = datetime.now()

    db.query(DeliveryOffer).filter(
        DeliveryOffer.partner_id == partner.id,
        DeliveryOffer.status == "Pending",
        DeliveryOffer.expires_at <= now,
    ).update(
        {"status": "Expired"},
        synchronize_session=False,
    )
    db.commit()

    return (
        db.query(DeliveryOffer)
        .filter(
            DeliveryOffer.partner_id == partner.id,
            DeliveryOffer.status == "Pending",
            DeliveryOffer.expires_at > now,
        )
        .order_by(DeliveryOffer.offered_at.desc())
        .all()
    )


@router.patch(
    "/offers/{offer_id}/respond",
    response_model=DeliveryOfferResponse,
)
async def respond_to_delivery_offer(
    offer_id: int,
    data: DeliveryOfferResponseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_delivery_partner(current_user)
    partner = get_partner(db, current_user.id)

    offer = (
        db.query(DeliveryOffer)
        .filter(
            DeliveryOffer.id == offer_id,
            DeliveryOffer.partner_id == partner.id,
        )
        .with_for_update()
        .first()
    )

    if not offer:
        raise HTTPException(
            status_code=404,
            detail="Delivery offer not found",
        )

    if offer.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail="This offer has already been responded to",
        )

    now = datetime.now()

    if offer.expires_at <= now:
        offer.status = "Expired"
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Delivery offer has expired",
        )

    try:
        if data.status == "Accepted":
            order = (
                db.query(Order)
                .filter(Order.id == offer.order_id)
                .with_for_update()
                .first()
            )

            if not order:
                raise HTTPException(
                    status_code=404,
                    detail="Order not found",
                )

            if order.status != OrderStatus.READY:
                raise HTTPException(
                    status_code=400,
                    detail="Only ready orders can be assigned",
                )

            if not partner.is_online or not partner.is_available:
                raise HTTPException(
                    status_code=400,
                    detail="You must be online and available",
                )

            existing_assignment = (
                db.query(DeliveryOffer)
                .filter(
                    DeliveryOffer.order_id == order.id,
                    DeliveryOffer.status == "Accepted",
                    DeliveryOffer.id != offer.id,
                )
                .first()
            )

            if existing_assignment:
                raise HTTPException(
                    status_code=409,
                    detail="This order has already been assigned",
                )

            offer.status = "Accepted"
            order.status = OrderStatus.ASSIGNED
            partner.is_available = False

            record_order_history(
                db,
                order,
                current_user,
                OrderStatus.ASSIGNED,
                "Delivery partner accepted the offer",
            )
        else:
            offer.status = "Rejected"

        offer.responded_at = now
        db.commit()
        db.refresh(offer)

        if data.status == "Accepted":
            await broadcast_order_update(order)

        return offer

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise


# -------------------- PICKUP --------------------

@router.patch("/orders/{order_id}/pickup")
async def pickup_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_delivery_partner(current_user)
    partner = get_partner(db, current_user.id)
    order = get_assigned_order(db, order_id, partner.id)

    if order.status != OrderStatus.ASSIGNED:
        raise HTTPException(
            status_code=400,
            detail="Only assigned orders can be picked up",
        )

    try:
        order.status = OrderStatus.PICKED_UP

        record_order_history(
            db,
            order,
            current_user,
            OrderStatus.PICKED_UP,
            "Order picked up by delivery partner",
        )

        db.commit()
        db.refresh(order)

        await broadcast_order_update(order)

        return {
            "message": "Order picked up successfully",
            "order_id": order.id,
            "status": order.status.value,
        }

    except Exception:
        db.rollback()
        raise


# -------------------- START DELIVERY --------------------

@router.patch("/orders/{order_id}/start-delivery")
async def start_delivery(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_delivery_partner(current_user)
    partner = get_partner(db, current_user.id)
    order = get_assigned_order(db, order_id, partner.id)

    if order.status != OrderStatus.PICKED_UP:
        raise HTTPException(
            status_code=400,
            detail="Pick up the order before starting delivery",
        )

    try:
        order.status = OrderStatus.OUT_FOR_DELIVERY

        record_order_history(
            db,
            order,
            current_user,
            OrderStatus.OUT_FOR_DELIVERY,
            "Order is out for delivery",
        )

        db.commit()
        db.refresh(order)

        await broadcast_order_update(order)

        return {
            "message": "Delivery started successfully",
            "order_id": order.id,
            "status": order.status.value,
        }

    except Exception:
        db.rollback()
        raise


# -------------------- COMPLETE DELIVERY WITH OTP --------------------

@router.patch("/orders/{order_id}/complete")
async def complete_delivery(
    order_id: int,
    otp: str = Query(..., min_length=4, max_length=8),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_delivery_partner(current_user)
    partner = get_partner(db, current_user.id)
    order = get_assigned_order(db, order_id, partner.id)

    if order.status != OrderStatus.OUT_FOR_DELIVERY:
        raise HTTPException(
            status_code=400,
            detail="Order must be out for delivery before completion",
        )

    if order.otp_locked:
        raise HTTPException(
            status_code=423,
            detail="OTP verification is locked for this order",
        )

    if not order.delivery_otp or str(order.delivery_otp) != otp:
        try:
            order.otp_attempts = (order.otp_attempts or 0) + 1

            if order.otp_attempts >= 5:
                order.otp_locked = True

            db.commit()

        except Exception:
            db.rollback()
            raise

        raise HTTPException(
            status_code=400,
            detail="Invalid delivery OTP",
        )

    try:
        order.status = OrderStatus.DELIVERED

        if order.payment_method.value == "COD":
            order.payment_status = "PAID"

        record_order_history(
            db,
            order,
            current_user,
            OrderStatus.DELIVERED,
            "Delivery completed after OTP verification",
        )

        # Convert both values to Decimal before adding.
        partner.total_earnings = (
            Decimal(str(partner.total_earnings or 0))
            + Decimal(str(order.delivery_fee or 0))
        )

        partner.is_available = True

        db.commit()
        db.refresh(order)

        await broadcast_order_update(order)

        return {
            "message": "Delivery completed successfully",
            "order_id": order.id,
            "status": order.status.value,
        }

    except Exception:
        db.rollback()
        raise