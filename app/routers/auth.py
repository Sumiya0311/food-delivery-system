from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.config import settings
from app.core.security import (
    verify_password,
    create_access_token,
    get_password_hash,
)


router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = HTTPBearer()




class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str
    role: UserRole = UserRole.CUSTOMER


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str
    role: UserRole
    is_approved: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)





@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    email = str(payload.email).strip().lower()
    phone = payload.phone.strip()

    if payload.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin registration is not allowed",
        )

    existing_user = db.query(User).filter(
        (User.email == email) | (User.phone == phone)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or phone number is already registered",
        )

    user = User(
        full_name=payload.full_name.strip(),
        email=email,
        phone=phone,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
        is_approved=(payload.role == UserRole.CUSTOMER),
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user




@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    email = str(payload.email).strip().lower()

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user or not verify_password(
        payload.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is awaiting administrator approval",
        )

    token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role.value,
        },
        expires_delta=timedelta(minutes=30),
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }




def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )

        subject = payload.get("sub")

        if subject is None:
            raise credentials_error

        user_id = int(subject)

    except (JWTError, TypeError, ValueError):
        raise credentials_error

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if (
        user is None
        or not user.is_active
        or not user.is_approved
    ):
        raise credentials_error

    return user




@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user