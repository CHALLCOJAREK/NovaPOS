from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductCategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    description: str | None = None


class ProductCategoryCreate(ProductCategoryBase):
    pass


class ProductCategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = None
    is_active: bool | None = None


class ProductCategoryResponse(ProductCategoryBase):
    id: int
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)