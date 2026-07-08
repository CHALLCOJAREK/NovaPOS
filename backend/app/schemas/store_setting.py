from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class StoreSettingBase(BaseModel):
    store_name: str = Field(..., min_length=2, max_length=150)
    business_name: str | None = Field(default=None, max_length=200)
    ruc: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=250)
    phone: str | None = Field(default=None, max_length=20)
    whatsapp: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=150)
    logo_path: str | None = Field(default=None, max_length=300)
    currency: str = Field(default="PEN", max_length=10)
    igv_percentage: Decimal = Field(default=Decimal("18.00"), ge=0, le=100)
    receipt_footer: str | None = Field(default=None, max_length=300)


class StoreSettingCreate(StoreSettingBase):
    pass


class StoreSettingUpdate(BaseModel):
    store_name: str | None = Field(default=None, min_length=2, max_length=150)
    business_name: str | None = Field(default=None, max_length=200)
    ruc: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=250)
    phone: str | None = Field(default=None, max_length=20)
    whatsapp: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=150)
    logo_path: str | None = Field(default=None, max_length=300)
    currency: str | None = Field(default=None, max_length=10)
    igv_percentage: Decimal | None = Field(default=None, ge=0, le=100)
    receipt_footer: str | None = Field(default=None, max_length=300)
    is_active: bool | None = None


class StoreSettingResponse(StoreSettingBase):
    id: int
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)