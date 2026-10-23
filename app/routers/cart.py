from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.menu_item import MenuItem
from app.models.restaurant import Restaurant
from app.models.user import User, UserRole
from app.schemas.cart import (
    CartItemAdd,
    CartItemUpdate,
    CartResponse,
)
from app.routers.auth import get_current_user


router = APIRouter(prefix="/cart", tags=["Shopping Cart"])


def require_customer(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can manage a cart",
        )
    return current_user


def get_or_create_cart(db: Session, customer_id: int) -> Cart:
    cart = (
        db.query(Cart)
        .options(selectinload(Cart.items))
        .filter(Cart.customer_id == customer_id)
        .first()
    )

    if cart is None:
        cart = Cart(customer_id=customer_id, restaurant_id=None)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart


@router.get("/", response_model=CartResponse)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    return get_or_create_cart(db, current_user.id)


@router.post("/items", response_model=CartResponse)
def add_cart_item(
    payload: CartItemAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    menu_item = (
        db.query(MenuItem)
        .join(Restaurant, MenuItem.restaurant_id == Restaurant.id)
        .filter(
            MenuItem.id == payload.menu_item_id,
            MenuItem.is_available.is_(True),
            MenuItem.is_deleted.is_(False),
            Restaurant.is_active.is_(True),
        )
        .first()
    )

    if menu_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Available menu item not found",
        )

    cart = get_or_create_cart(db, current_user.id)

    if cart.restaurant_id not in (None, menu_item.restaurant_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your cart contains items from another restaurant. Clear it before adding items from a different restaurant.",
        )

    cart.restaurant_id = menu_item.restaurant_id

    existing_item = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id,
            CartItem.menu_item_id == menu_item.id,
        )
        .first()
    )

    if existing_item:
        new_quantity = existing_item.quantity + payload.quantity

        if new_quantity > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The total quantity of a menu item cannot exceed 10",
            )

        existing_item.quantity = new_quantity
    else:
        db.add(
            CartItem(
                cart_id=cart.id,
                menu_item_id=menu_item.id,
                quantity=payload.quantity,
            )
        )

    db.commit()

    return get_or_create_cart(db, current_user.id)


@router.patch("/items/{item_id}", response_model=CartResponse)
def update_cart_item(
    item_id: int,
    payload: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    cart = get_or_create_cart(db, current_user.id)

    item = (
        db.query(CartItem)
        .filter(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id,
        )
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    item.quantity = payload.quantity
    db.commit()

    return get_or_create_cart(db, current_user.id)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    cart = get_or_create_cart(db, current_user.id)

    item = (
        db.query(CartItem)
        .filter(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id,
        )
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    db.delete(item)
    db.flush()

    remaining_items = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id)
        .count()
    )

    if remaining_items == 0:
        cart.restaurant_id = None

    db.commit()
    return None


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    cart = (
        db.query(Cart)
        .filter(Cart.customer_id == current_user.id)
        .first()
    )

    if cart is None:
        return None

    db.query(CartItem).filter(
        CartItem.cart_id == cart.id
    ).delete(synchronize_session=False)

    cart.restaurant_id = None
    db.commit()

    return None