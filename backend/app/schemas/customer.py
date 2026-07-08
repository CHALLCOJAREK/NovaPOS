from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class CustomerBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    document_number: str | None = Field(default=None, max_length=20)
    phone: str | None = Field(default=None, max_length=20)
    whatsapp: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = Field(default=None, max_length=120)
    address: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    document_number: str | None = Field(default=None, max_length=20)
    phone: str | None = Field(default=None, max_length=20)
    whatsapp: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = Field(default=None, max_length=120)
    address: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    is_active: bool | None = None


class CustomerResponse(CustomerBase):
    id: int
    total_purchased: float
    total_debt: float
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }