from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RoleBase(BaseModel):
    """
    Base schema for Role.
    """

    name: str
    description: str | None = None


class RoleCreate(RoleBase):
    """
    Schema for creating roles.
    """

    pass


class RoleUpdate(BaseModel):
    """
    Schema for updating roles.
    """

    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class RoleResponse(RoleBase):
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