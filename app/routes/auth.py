from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.core.utils import error_response, success_response
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserLogin, UserResponse, UserSignup

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _set_auth_cookie(response: Response, token: str) -> None:
    """Store JWT in a secure HttpOnly cookie (not exposed to JavaScript)."""
    max_age = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=max_age,
        path="/",
    )


def _clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.COOKIE_NAME,
        path="/",
        samesite="lax",
    )


def _user_data(user: User) -> dict:
    return UserResponse.model_validate(user).model_dump(mode="json")


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )

    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response("Email is already registered"),
        )

    db.refresh(new_user)
    return success_response(
        message="Account created successfully",
        data={"user": _user_data(new_user)},
    )


@router.post("/login")
def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if user is None or not verify_password(user_data.password, user.hashed_password):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response("Invalid email or password"),
        )

    token = create_access_token(subject=user.email)
    _set_auth_cookie(response, token)

    return success_response(
        message="Login successful",
        data={"user": _user_data(user)},
    )


@router.post("/logout")
def logout(response: Response):
    _clear_auth_cookie(response)
    return success_response(message="Logged out successfully", data=None)


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return success_response(
        message="User fetched successfully",
        data={"user": _user_data(current_user)},
    )
