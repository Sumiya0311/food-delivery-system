from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.address import Address
from app.models.user import User, UserRole
from app.schemas.address import AddressCreate, AddressResponse
from app.routers.auth import get_current_user


router = APIRouter(prefix="/addresses", tags=["Addresses"])


def require_customer(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can manage delivery addresses",
        )
    return current_user


@router.post(
    "/",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_address(
    payload: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    if payload.is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id
        ).update({"is_default": False})

    address = Address(
        user_id=current_user.id,
        label=payload.label,
        recipient_name=payload.recipient_name,
        phone=payload.phone,
        address_line=payload.address_line,
        city=payload.city,
        pincode=payload.pincode,
        latitude=payload.latitude,
        longitude=payload.longitude,
        is_default=payload.is_default,
    )

    db.add(address)
    db.commit()
    db.refresh(address)

    return address


@router.get("/", response_model=list[AddressResponse])
def list_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    return (
        db.query(Address)
        .filter(Address.user_id == current_user.id)
        .order_by(Address.is_default.desc(), Address.id.desc())
        .all()
    )


@router.get("/{address_id}", response_model=AddressResponse)
def get_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id,
    ).first()

    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    return address


@router.put("/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: int,
    payload: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id,
    ).first()

    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    if payload.is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.id != address_id,
        ).update({"is_default": False})

    address.label = payload.label
    address.recipient_name = payload.recipient_name
    address.phone = payload.phone
    address.address_line = payload.address_line
    address.city = payload.city
    address.pincode = payload.pincode
    address.latitude = payload.latitude
    address.longitude = payload.longitude
    address.is_default = payload.is_default

    db.commit()
    db.refresh(address)

    return address


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id,
    ).first()

    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    db.delete(address)
    db.commit()

    return None