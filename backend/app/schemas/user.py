from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.role import RoleResponse


class UserBase(BaseModel):
    """
    Base schema for User.
    """

    username: str
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """
    Schema for creating users.
    """

    password: str
    role_id: int


class UserUpdate(BaseModel):
    """
    Schema for updating users.
    """

    username: str | None = None
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None
    role_id: int | None = None
    is_active: bool | None = None


class UserLogin(BaseModel):
    """
    Schema for authentication.
    """

    username: str
    password: str


class UserResponse(UserBase):
    """
    Schema returned by API.

    Never expose hashed_password.
    """

    id: int
    role_id: int
    role: RoleResponse | None = None

    is_active: bool
    is_deleted: bool

    last_login_at: datetime | None

    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )