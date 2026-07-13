from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel

from app.schemas.customer_debt_payment import CustomerDebtPaymentResponse


class CustomerDebtBase(BaseModel):
    customer_id: int
    sale_id: int
    original_amount: Decimal
    paid_amount: Decimal
    pending_amount: Decimal
    status: str


class CustomerDebtCreate(BaseModel):
    customer_id: int
    sale_id: int
    original_amount: Decimal


class CustomerDebtResponse(CustomerDebtBase):
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    payments: Optional[List[CustomerDebtPaymentResponse]] = []

    class Config:
        from_attributes = True