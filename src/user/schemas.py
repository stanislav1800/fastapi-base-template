from datetime import datetime
from typing import Optional

from uuid import UUID
from pydantic import BaseModel


class User(BaseModel):
    id: Optional[UUID]
    email: str
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created_at: datetime


class UserResponse(BaseModel):
    id: Optional[UUID]
    email: str
    is_active: bool
    created_at: datetime


class UserCreate(BaseModel):
    email: str
    hashed_password: str
    is_active: bool = True


class UserCreateBody(BaseModel):
    email: str
    password: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserUpdate(BaseModel):
    id: UUID
    email: str
    is_active: bool = True


class UserUpdateBody(BaseModel):
    email: Optional[str] = None
    is_active: Optional[bool] = True
