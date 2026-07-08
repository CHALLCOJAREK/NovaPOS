from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    image_path: str | None = Field(default=None, max_length=255)
    internal_code: str | None = Field(default=None, max_length=50)
    barcode: str | None = Field(default=None, max_length=100)

    name: str = Field(..., min_length=2, max_length=150)
    brand: str | None = Field(default=None, max_length=100)

    category_id: int = Field(..., gt=0)
    supplier_id: int | None = Field(default=None, gt=0)

    cost_price: Decimal = Field(default=0, ge=0)
    sale_price: Decimal = Field(default=0, ge=0)
    profit_margin: Decimal = Field(default=0, ge=0)
    profit_amount: Decimal = Field(default=0, ge=0)

    stock: Decimal = Field(default=0, ge=0)
    minimum_stock: Decimal = Field(default=0, ge=0)

    expiration_date: date | None = None
    batch: str | None = Field(default=None, max_length=100)

    is_weighted: bool = False
    is_frozen: bool = False

    status: str = Field(default="ACTIVE", max_length=30)
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    image_path: str | None = Field(default=None, max_length=255)
    internal_code: str | None = Field(default=None, max_length=50)
    barcode: str | None = Field(default=None, max_length=100)

    name: str | None = Field(default=None, min_length=2, max_length=150)
    brand: str | None = Field(default=None, max_length=100)

    category_id: int | None = Field(default=None, gt=0)
    supplier_id: int | None = Field(default=None, gt=0)

    cost_price: Decimal | None = Field(default=None, ge=0)
    sale_price: Decimal | None = Field(default=None, ge=0)
    profit_margin: Decimal | None = Field(default=None, ge=0)
    profit_amount: Decimal | None = Field(default=None, ge=0)

    stock: Decimal | None = Field(default=None, ge=0)
    minimum_stock: Decimal | None = Field(default=None, ge=0)

    expiration_date: date | None = None
    batch: str | None = Field(default=None, max_length=100)

    is_weighted: bool | None = None
    is_frozen: bool | None = None

    status: str | None = Field(default=None, max_length=30)
    is_active: bool | None = None


class ProductResponse(ProductBase):
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)