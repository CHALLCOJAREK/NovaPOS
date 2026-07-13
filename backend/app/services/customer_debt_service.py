from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.customer_debt import CustomerDebt
from app.models.customer_debt_payment import CustomerDebtPayment
from app.schemas.customer_debt import CustomerDebtCreate
from app.schemas.customer_debt_payment import CustomerDebtPaymentCreate
from app.repositories.customer_debt_repository import CustomerDebtRepository
from app.services.cash_service import CashService
from app.models.cash_register import CashRegister

class CustomerDebtService:


    @staticmethod
    def create_debt(
        db: Session,
        data: CustomerDebtCreate
    ):

        debt = CustomerDebt(
            customer_id=data.customer_id,
            sale_id=data.sale_id,
            original_amount=data.original_amount,
            paid_amount=Decimal("0.00"),
            pending_amount=data.original_amount,
            status="PENDING"
        )

        return CustomerDebtRepository.create(
            db,
            debt
        )


    @staticmethod
    def get_all(
        db: Session
    ):

        return CustomerDebtRepository.get_all(db)


    @staticmethod
    def get_by_customer(
        db: Session,
        customer_id: int
    ):

        return CustomerDebtRepository.get_by_customer(
            db,
            customer_id
        )


    @staticmethod
    def register_payment(
        db: Session,
        debt_id: int,
        data: CustomerDebtPaymentCreate
    ):

        debt = CustomerDebtRepository.get_by_id(
            db,
            debt_id
        )

        if not debt:
            raise HTTPException(
                status_code=404,
                detail="Deuda no encontrada"
            )


        if debt.status == "PAID":
            raise HTTPException(
                status_code=400,
                detail="La deuda ya fue pagada"
            )


        if data.amount > debt.pending_amount:
            raise HTTPException(
                status_code=400,
                detail="El pago supera la deuda pendiente"
            )


        current_cash = (
            db.query(CashRegister)
            .filter(
                CashRegister.status == "OPEN",
                CashRegister.is_deleted == False
            )
            .first()
        )


        payment = CustomerDebtPayment(
            customer_debt_id=debt.id,
            payment_method=data.payment_method,
            amount=data.amount,
            cash_register_id=current_cash.id if current_cash else None,
            notes=data.notes
        )


        CustomerDebtRepository.create_payment(
            db,
            payment
        )


        debt.paid_amount += data.amount
        debt.pending_amount -= data.amount


        if debt.pending_amount == Decimal("0.00"):
            debt.status = "PAID"

        else:
            debt.status = "PARTIAL"


        CustomerDebtRepository.update(
            db,
            debt
        )


        CashService(db).register_sale_payment(
            sale_id=debt.sale_id,
            payment_method=data.payment_method,
            total_amount=data.amount,
            profit_amount=Decimal("0.00")
        )

        return debt


    @staticmethod
    def get_payments(
        db: Session,
        debt_id: int
    ):

        return CustomerDebtRepository.get_payments(
            db,
            debt_id
        )