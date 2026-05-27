"""In-memory user store with password hashing."""

from __future__ import annotations

import uuid

from passlib.context import CryptContext

from backend.auth.models import UserCreate, UserResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class _UserRecord:
    __slots__ = ("id", "username", "email", "role", "hashed_password", "is_active")

    def __init__(
        self,
        user_id: str,
        username: str,
        email: str,
        role: str,
        hashed_password: str,
    ) -> None:
        self.id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.hashed_password = hashed_password
        self.is_active = True


_users: dict[str, _UserRecord] = {}


class UserStore:
    """Simple user store backed by an in-memory dict."""

    def create(self, data: UserCreate) -> UserResponse:
        if any(u.username == data.username for u in _users.values()):
            raise ValueError(f"Username '{data.username}' already exists")
        if any(u.email == data.email for u in _users.values()):
            raise ValueError(f"Email '{data.email}' already registered")

        user_id = str(uuid.uuid4())
        record = _UserRecord(
            user_id=user_id,
            username=data.username,
            email=data.email,
            role=data.role,
            hashed_password=pwd_context.hash(data.password),
        )
        _users[user_id] = record
        return UserResponse(
            id=record.id,
            username=record.username,
            email=record.email,
            role=record.role,
            is_active=record.is_active,
        )

    def authenticate(self, username: str, password: str) -> UserResponse | None:
        for record in _users.values():
            if record.username == username and pwd_context.verify(password, record.hashed_password):
                return UserResponse(
                    id=record.id,
                    username=record.username,
                    email=record.email,
                    role=record.role,
                    is_active=record.is_active,
                )
        return None

    def get_by_username(self, username: str) -> UserResponse | None:
        for record in _users.values():
            if record.username == username:
                return UserResponse(
                    id=record.id,
                    username=record.username,
                    email=record.email,
                    role=record.role,
                    is_active=record.is_active,
                )
        return None

    def list_users(self) -> list[UserResponse]:
        return [
            UserResponse(
                id=r.id,
                username=r.username,
                email=r.email,
                role=r.role,
                is_active=r.is_active,
            )
            for r in _users.values()
        ]
