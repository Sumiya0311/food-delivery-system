from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.restaurant import Restaurant
from app.models.user import User, UserRole
from app.schemas.restaurant import RestaurantCreate, RestaurantResponse
from app.routers.auth import get_current_user


router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.post(
    "/",
    response_model=RestaurantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_restaurant(
    payload: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.RESTAURANT_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurant owners can create restaurants",
        )

    restaurant = Restaurant(
        owner_id=current_user.id,
        name=payload.name,
        description=payload.description,
        address=payload.address,
        latitude=payload.latitude,
        longitude=payload.longitude,
        delivery_radius_km=payload.delivery_radius_km,
        opening_time=payload.opening_time,
        closing_time=payload.closing_time,
        estimated_prep_minutes=payload.estimated_prep_minutes,
        is_open=False,
        is_active=True,
    )

    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)

    return restaurant


@router.get("/", response_model=list[RestaurantResponse])
def list_restaurants(
    db: Session = Depends(get_db),
):
    return (
        db.query(Restaurant)
        .filter(
            Restaurant.is_active.is_(True),
            Restaurant.is_open.is_(True),
        )
        .order_by(Restaurant.name)
        .all()
    )


@router.get("/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
):
    restaurant = (
        db.query(Restaurant)
        .filter(
            Restaurant.id == restaurant_id,
            Restaurant.is_active.is_(True),
        )
        .first()
    )

    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    return restaurant