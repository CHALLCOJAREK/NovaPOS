from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.customer_debt import CustomerDebtResponse
from app.schemas.customer_debt_payment import (
    CustomerDebtPaymentCreate,
    CustomerDebtPaymentResponse
)

from app.services.customer_debt_service import CustomerDebtService


router = APIRouter(
    prefix="/customer-debts",
    tags=["Customer Debts"]
)


@router.get(
    "/",
    response_model=List[CustomerDebtResponse]
)
def get_customer_debts(
    db: Session = Depends(get_db)
):

    return CustomerDebtService.get_all(db)


@router.get(
    "/customer/{customer_id}",
    response_model=List[CustomerDebtResponse]
)
def get_customer_debts_by_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):

    return CustomerDebtService.get_by_customer(
        db,
        customer_id
    )


@router.post(
    "/{debt_id}/payments",
    response_model=CustomerDebtResponse
)
def pay_customer_debt(
    debt_id: int,
    data: CustomerDebtPaymentCreate,
    db: Session = Depends(get_db)
):

    return CustomerDebtService.register_payment(
        db,
        debt_id,
        data
    )


@router.get(
    "/{debt_id}/payments",
    response_model=List[CustomerDebtPaymentResponse]
)
def get_customer_debt_payments(
    debt_id: int,
    db: Session = Depends(get_db)
):

    return CustomerDebtService.get_payments(
        db,
        debt_id
    )