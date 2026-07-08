from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PermissionBase(BaseModel):
    """
    Base schema for Permission.
    """

    code: str
    name: str
    description: str | None = None
    module: str


class PermissionCreate(PermissionBase):
    """
    Schema for creating permissions.
    """

    pass


class PermissionUpdate(BaseModel):
    """
    Schema for updating permissions.
    """

    code: str | None = None
    name: str | None = None
    description: str | None = None
    module: str | None = None
    is_active: bool | None = None


class PermissionResponse(PermissionBase):
    """
    Schema returned by API.
    """

    id: int
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )