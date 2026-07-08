from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PurchaseItemBase(BaseModel):
    product_id: int
    package_total_cost: Decimal = Field(gt=0)
    unit_quantity: Decimal = Field(gt=0)
    expiration_date: Optional[date] = None
    batch: Optional[str] = None
    notes: Optional[str] = None


class PurchaseItemCreate(PurchaseItemBase):
    pass


class PurchaseItemResponse(PurchaseItemBase):
    id: int
    purchase_id: int
    unit_cost: Decimal
    previous_cost: Decimal
    new_cost: Decimal
    previous_stock: Decimal
    new_stock: Decimal
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PurchaseBase(BaseModel):
    supplier_id: int
    document_type: str = Field(min_length=2, max_length=30)
    document_number: Optional[str] = Field(default=None, max_length=50)
    purchase_date: date
    notes: Optional[str] = None
    ocr_source_path: Optional[str] = Field(default=None, max_length=255)


class PurchaseCreate(PurchaseBase):
    items: list[PurchaseItemCreate] = Field(min_length=1)


class PurchaseResponse(PurchaseBase):
    id: int
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    is_confirmed: bool
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: list[PurchaseItemResponse] = []

    model_config = ConfigDict(from_attributes=True)