from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.order import Order
from app.models.order_status_history import OrderStatusHistory
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.order_status_history import OrderStatusHistoryResponse

router = APIRouter(
    prefix="/orders",
    tags=["Order History"],
)


@router.get(
    "/{order_id}/history",
    response_model=list[OrderStatusHistoryResponse],
)
def get_order_history(
    order_id: int,
    status: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    role = current_user.role.value

    if role == "Customer" and order.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot view this order history",
        )

    if role == "Restaurant Owner":
        from app.models.restaurant import Restaurant

        restaurant = (
            db.query(Restaurant)
            .filter(
                Restaurant.owner_id == current_user.id,
                Restaurant.id == order.restaurant_id,
            )
            .first()
        )

        if not restaurant:
            raise HTTPException(
                status_code=403,
                detail="You cannot view this order history",
            )

    if role == "Delivery Partner":
        from app.models.delivery_partner import DeliveryPartner
        from app.models.delivery_offer import DeliveryOffer

        partner = (
            db.query(DeliveryPartner)
            .filter(DeliveryPartner.user_id == current_user.id)
            .first()
        )

        offer = None
        if partner:
            offer = (
                db.query(DeliveryOffer)
                .filter(
                    DeliveryOffer.order_id == order.id,
                    DeliveryOffer.partner_id == partner.id,
                )
                .first()
            )

        if not offer:
            raise HTTPException(
                status_code=403,
                detail="You cannot view this order history",
            )

    query = db.query(OrderStatusHistory).filter(
        OrderStatusHistory.order_id == order_id
    )

    if status:
        query = query.filter(
            OrderStatusHistory.status.ilike(status.strip())
        )

    return (
        query.order_by(
            OrderStatusHistory.created_at.asc(),
            OrderStatusHistory.id.asc(),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )