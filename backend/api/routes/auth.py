"""Authentication endpoints — signup, login, and user info."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from backend.auth.jwt import create_access_token, get_current_user
from backend.auth.models import TokenResponse, UserCreate, UserLogin, UserResponse
from backend.auth.store import UserStore
from backend.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

_store = UserStore()


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(data: UserCreate) -> TokenResponse:
    try:
        user = _store.create(data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    token = create_access_token({"sub": user.username, "role": user.role})
    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_expire_minutes * 60,
        user=user,
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin) -> TokenResponse:
    user = _store.authenticate(data.username, data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token({"sub": user.username, "role": user.role})
    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_expire_minutes * 60,
        user=user,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: UserResponse | None = Depends(get_current_user)) -> UserResponse:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user


@router.get("/users", response_model=list[UserResponse])
async def list_users() -> list[UserResponse]:
    return _store.list_users()
