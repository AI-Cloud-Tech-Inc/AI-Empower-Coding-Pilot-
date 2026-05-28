"""User store with database persistence and password hashing."""

from __future__ import annotations

import uuid

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.models import UserCreate, UserResponse
from backend.models.db_models import UserDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserStore:
    """User store backed by SQLAlchemy async sessions."""

    async def create(self, db: AsyncSession, data: UserCreate) -> UserResponse:
        existing = await db.execute(select(UserDB).where(UserDB.username == data.username))
        if existing.scalar_one_or_none():
            raise ValueError(f"Username '{data.username}' already exists")

        existing_email = await db.execute(select(UserDB).where(UserDB.email == data.email))
        if existing_email.scalar_one_or_none():
            raise ValueError(f"Email '{data.email}' already registered")

        user = UserDB(
            id=str(uuid.uuid4()),
            username=data.username,
            email=data.email,
            role=data.role,
            hashed_password=pwd_context.hash(data.password),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
        )

    async def authenticate(
        self, db: AsyncSession, username: str, password: str
    ) -> UserResponse | None:
        result = await db.execute(select(UserDB).where(UserDB.username == username))
        user = result.scalar_one_or_none()
        if user is None or not pwd_context.verify(password, user.hashed_password):
            return None
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
        )

    async def get_by_username(self, db: AsyncSession, username: str) -> UserResponse | None:
        result = await db.execute(select(UserDB).where(UserDB.username == username))
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
        )

    async def list_users(self, db: AsyncSession) -> list[UserResponse]:
        result = await db.execute(select(UserDB))
        return [
            UserResponse(
                id=u.id,
                username=u.username,
                email=u.email,
                role=u.role,
                is_active=u.is_active,
            )
            for u in result.scalars().all()
        ]
