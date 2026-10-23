from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.menu_item import MenuItem
from app.models.restaurant import Restaurant
from app.models.user import User, UserRole
from app.schemas.menu_item import MenuItemCreate, MenuItemResponse
from app.routers.auth import get_current_user


router = APIRouter(prefix="/menu-items", tags=["Menu Items"])


@router.post(
    "/",
    response_model=MenuItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_menu_item(
    payload: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.RESTAURANT_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurant owners can add menu items",
        )

    restaurant = (
        db.query(Restaurant)
        .filter(
            Restaurant.id == payload.restaurant_id,
            Restaurant.owner_id == current_user.id,
            Restaurant.is_active.is_(True),
        )
        .first()
    )

    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found or you do not own this restaurant",
        )

    item = MenuItem(
        restaurant_id=restaurant.id,
        name=payload.name.strip(),
        description=payload.description,
        category=payload.category.strip(),
        price=payload.price,
        is_available=payload.is_available,
        is_deleted=False,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@router.get(
    "/restaurant/{restaurant_id}",
    response_model=list[MenuItemResponse],
)
def list_menu_items(
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

    return (
        db.query(MenuItem)
        .filter(
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.is_available.is_(True),
            MenuItem.is_deleted.is_(False),
        )
        .order_by(MenuItem.name)
        .all()
    )


@router.patch("/{item_id}", response_model=MenuItemResponse)
def update_menu_item(
    item_id: int,
    payload: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.RESTAURANT_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurant owners can update menu items",
        )

    item = (
        db.query(MenuItem)
        .join(Restaurant, MenuItem.restaurant_id == Restaurant.id)
        .filter(
            MenuItem.id == item_id,
            Restaurant.owner_id == current_user.id,
        )
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found or you do not own it",
        )

    if payload.restaurant_id != item.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A menu item cannot be moved to another restaurant",
        )

    item.name = payload.name.strip()
    item.description = payload.description
    item.category = payload.category.strip()
    item.price = payload.price
    item.is_available = payload.is_available

    db.commit()
    db.refresh(item)

    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.RESTAURANT_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurant owners can delete menu items",
        )

    item = (
        db.query(MenuItem)
        .join(Restaurant, MenuItem.restaurant_id == Restaurant.id)
        .filter(
            MenuItem.id == item_id,
            Restaurant.owner_id == current_user.id,
        )
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found or you do not own it",
        )

    item.is_deleted = True
    item.is_available = False

    db.commit()
    return None