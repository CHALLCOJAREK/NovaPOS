from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: Decimal = Field(gt=0)


class SaleCreate(BaseModel):
    customer_id: int | None = None

    document_type: str = Field(
        default="NOTA_VENTA"
    )

    payment_method: str = Field(
        default="CASH"
    )

    discount_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0
    )

    notes: str | None = None

    items: list[SaleItemCreate]


class SaleItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    unit_cost: Decimal
    subtotal: Decimal
    cost_total: Decimal
    profit_amount: Decimal

    model_config = ConfigDict(
        from_attributes=True
    )


class SaleResponse(BaseModel):
    id: int

    customer_id: int | None

    document_type: str
    payment_method: str

    subtotal: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    total_cost: Decimal
    profit_amount: Decimal

    notes: str | None

    is_confirmed: bool
    is_deleted: bool

    created_at: datetime
    updated_at: datetime | None

    items: list[SaleItemResponse] = []

    model_config = ConfigDict(
        from_attributes=True
    )