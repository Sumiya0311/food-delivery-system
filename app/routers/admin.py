from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.routers.auth import get_current_user


router = APIRouter(prefix="/admin", tags=["Admin"])


def require_admin(
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform this action",
        )
    return current_user


@router.get("/pending-users")
def get_pending_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    users = (
        db.query(User)
        .filter(
            User.is_approved.is_(False),
            User.role.in_([
                UserRole.RESTAURANT_OWNER,
                UserRole.DELIVERY_PARTNER,
            ]),
        )
        .order_by(User.id)
        .all()
    )

    return [
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role.value,
            "is_approved": user.is_approved,
        }
        for user in users
    ]


@router.patch("/approve-user/{user_id}")
def approve_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.role not in (
        UserRole.RESTAURANT_OWNER,
        UserRole.DELIVERY_PARTNER,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only restaurant owners and delivery partners require approval",
        )

    if user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already approved",
        )

    user.is_approved = True
    db.commit()
    db.refresh(user)

    return {
        "message": "User approved successfully",
        "user_id": user.id,
        "role": user.role.value,
        "is_approved": user.is_approved,
    }