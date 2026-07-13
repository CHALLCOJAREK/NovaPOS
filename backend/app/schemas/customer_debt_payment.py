from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class CustomerDebtPaymentBase(BaseModel):
    customer_debt_id: int
    payment_method: str
    amount: Decimal
    cash_register_id: Optional[int] = None
    user_id: Optional[int] = None
    notes: Optional[str] = None


class CustomerDebtPaymentCreate(BaseModel):
    payment_method: str
    amount: Decimal
    notes: Optional[str] = None


class CustomerDebtPaymentResponse(CustomerDebtPaymentBase):
    id: int
    is_deleted: bool
    created_at: datetime

    class Config:
        from_attributes = True