from sqlalchemy.orm import Session

from app.models.customer_debt import CustomerDebt
from app.models.customer_debt_payment import CustomerDebtPayment


class CustomerDebtRepository:


    @staticmethod
    def create(
        db: Session,
        debt: CustomerDebt
    ):
        db.add(debt)
        db.commit()
        db.refresh(debt)

        return debt


    @staticmethod
    def get_all(
        db: Session
    ):
        return (
            db.query(CustomerDebt)
            .filter(CustomerDebt.is_deleted == False)
            .all()
        )


    @staticmethod
    def get_by_id(
        db: Session,
        debt_id: int
    ):
        return (
            db.query(CustomerDebt)
            .filter(
                CustomerDebt.id == debt_id,
                CustomerDebt.is_deleted == False
            )
            .first()
        )


    @staticmethod
    def get_by_customer(
        db: Session,
        customer_id: int
    ):
        return (
            db.query(CustomerDebt)
            .filter(
                CustomerDebt.customer_id == customer_id,
                CustomerDebt.is_deleted == False
            )
            .all()
        )


    @staticmethod
    def create_payment(
        db: Session,
        payment: CustomerDebtPayment
    ):
        db.add(payment)
        db.commit()
        db.refresh(payment)

        return payment


    @staticmethod
    def get_payments(
        db: Session,
        debt_id: int
    ):
        return (
            db.query(CustomerDebtPayment)
            .filter(
                CustomerDebtPayment.customer_debt_id == debt_id,
                CustomerDebtPayment.is_deleted == False
            )
            .all()
        )


    @staticmethod
    def update(
        db: Session,
        debt: CustomerDebt
    ):
        db.commit()
        db.refresh(debt)

        return debt