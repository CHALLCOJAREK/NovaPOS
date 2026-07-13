from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CashRegisterOpen(BaseModel):
    opening_amount: Decimal = Field(default=0, ge=0)
    opened_by_user_id: int | None = None
    notes: str | None = None


class CashRegisterClose(BaseModel):
    counted_cash_amount: Decimal = Field(ge=0)
    confirmed_yape_amount: Decimal = Field(default=0, ge=0)
    closed_by_user_id: int | None = None
    close_notes: str | None = None


class CashRegisterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    opened_by_user_id: int | None
    closed_by_user_id: int | None
    opened_at: datetime
    closed_at: datetime | None

    opening_amount: Decimal
    cash_sales_amount: Decimal
    yape_sales_amount: Decimal
    credit_sales_amount: Decimal

    manual_income_amount: Decimal
    manual_expense_amount: Decimal

    expected_cash_amount: Decimal
    counted_cash_amount: Decimal | None
    cash_difference_amount: Decimal | None

    expected_yape_amount: Decimal
    confirmed_yape_amount: Decimal | None
    yape_difference_amount: Decimal | None

    total_sales_amount: Decimal
    total_profit_amount: Decimal

    status: Literal["OPEN", "CLOSED"]

    notes: str | None
    close_notes: str | None

    is_deleted: bool
    created_at: datetime
    updated_at: datetime | None