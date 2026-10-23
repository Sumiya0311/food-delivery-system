from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.order import Order
from app.models.rating import Rating
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.rating import RatingCreate, RatingResponse

router = APIRouter(
    prefix="/ratings",
    tags=["Ratings and Reviews"],
)


@router.post("/", response_model=RatingResponse, status_code=201)
def create_rating(
    data: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.value != "Customer":
        raise HTTPException(
            status_code=403,
            detail="Only customers can submit ratings",
        )

    order = (
        db.query(Order)
        .filter(
            Order.id == data.order_id,
            Order.customer_id == current_user.id,
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found for this customer",
        )

    if order.status.value != "Delivered":
        raise HTTPException(
            status_code=400,
            detail="You can rate an order only after delivery",
        )

    existing_rating = (
        db.query(Rating)
        .filter(Rating.order_id == order.id)
        .first()
    )

    if existing_rating:
        raise HTTPException(
            status_code=409,
            detail="This order has already been rated",
        )

    rating = Rating(
        order_id=order.id,
        customer_id=current_user.id,
        restaurant_id=order.restaurant_id,
        rating=data.rating,
        review=data.review,
    )

    db.add(rating)
    db.commit()
    db.refresh(rating)

    return rating


@router.get(
    "/restaurant/{restaurant_id}",
    response_model=list[RatingResponse],
)
def get_restaurant_ratings(
    restaurant_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    from app.models.restaurant import Restaurant

    restaurant = (
        db.query(Restaurant)
        .filter(Restaurant.id == restaurant_id)
        .first()
    )

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found",
        )

    return (
        db.query(Rating)
        .filter(Rating.restaurant_id == restaurant_id)
        .order_by(Rating.created_at.desc(), Rating.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/my", response_model=list[RatingResponse])
def get_my_ratings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.value != "Customer":
        raise HTTPException(
            status_code=403,
            detail="Only customers can view their ratings",
        )

    return (
        db.query(Rating)
        .filter(Rating.customer_id == current_user.id)
        .order_by(Rating.created_at.desc(), Rating.id.desc())
        .all()
    )
@router.get("/restaurant/{restaurant_id}/summary")
def get_restaurant_rating_summary(
    restaurant_id: int,
    db: Session = Depends(get_db),
):
    from app.models.restaurant import Restaurant

    restaurant = (
        db.query(Restaurant)
        .filter(Restaurant.id == restaurant_id)
        .first()
    )

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found",
        )

    result = (
        db.query(
            func.count(Rating.id),
            func.avg(Rating.rating),
        )
        .filter(Rating.restaurant_id == restaurant_id)
        .first()
    )

    total_reviews = result[0] or 0
    average_rating = (
        round(float(result[1]), 2)
        if result[1] is not None
        else 0.0
    )

    return {
        "restaurant_id": restaurant_id,
        "average_rating": average_rating,
        "total_reviews": total_reviews,
    }
@router.get("/restaurant/{restaurant_id}/owner-summary")
def get_owner_rating_summary(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func
    from app.models.restaurant import Restaurant

    if current_user.role.value != "Restaurant Owner":
        raise HTTPException(
            status_code=403,
            detail="Only restaurant owners can access this endpoint",
        )

    restaurant = (
        db.query(Restaurant)
        .filter(
            Restaurant.id == restaurant_id,
            Restaurant.owner_id == current_user.id,
        )
        .first()
    )

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found or you do not own it",
        )

    total_reviews, average_rating = (
        db.query(
            func.count(Rating.id),
            func.avg(Rating.rating),
        )
        .filter(Rating.restaurant_id == restaurant_id)
        .first()
    )

    return {
        "restaurant_id": restaurant_id,
        "average_rating": (
            round(float(average_rating), 2)
            if average_rating is not None
            else 0.0
        ),
        "total_reviews": total_reviews or 0,
    }