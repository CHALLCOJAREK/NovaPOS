# app/schemas/supplier.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SupplierBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    ruc: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=30)
    whatsapp: Optional[str] = Field(default=None, max_length=30)
    email: Optional[EmailStr] = Field(default=None, max_length=120)
    contact_name: Optional[str] = Field(default=None, max_length=120)
    notes: Optional[str] = Field(default=None, max_length=500)


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    ruc: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=30)
    whatsapp: Optional[str] = Field(default=None, max_length=30)
    email: Optional[EmailStr] = Field(default=None, max_length=120)
    contact_name: Optional[str] = Field(default=None, max_length=120)
    notes: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = None


class SupplierResponse(SupplierBase):
    id: int
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)