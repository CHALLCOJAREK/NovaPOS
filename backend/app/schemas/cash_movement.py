from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CashMovementCreate(BaseModel):
    movement_type: Literal["MANUAL_INCOME", "MANUAL_EXPENSE"]
    payment_method: Literal["CASH", "YAPE"] = "CASH"
    amount: Decimal = Field(gt=0)
    reason: str = Field(min_length=3, max_length=150)
    user_id: int | None = None
    notes: str | None = None


class CashMovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cash_register_id: int
    movement_type: str
    payment_method: str | None
    amount: Decimal
    reason: str
    reference_type: str | None
    reference_id: int | None
    user_id: int | None
    notes: str | None
    is_deleted: bool
    created_at: datetime