from sqlalchemy.orm import Session

from app.models.cash_register import CashRegister
from app.models.cash_movement import CashMovement


class CashRepository:

    def __init__(self, db: Session):
        self.db = db

    # =============================
    # CASH REGISTER
    # =============================

    def get_open_register(self):
        return (
            self.db.query(CashRegister)
            .filter(
                CashRegister.status == "OPEN",
                CashRegister.is_deleted == False,
            )
            .first()
        )

    def get_all_registers(self):
        return (
            self.db.query(CashRegister)
            .filter(
                CashRegister.is_deleted == False,
            )
            .order_by(CashRegister.id.desc())
            .all()
        )

    def get_register_by_id(
        self,
        cash_register_id: int,
    ):
        return (
            self.db.query(CashRegister)
            .filter(
                CashRegister.id == cash_register_id,
                CashRegister.is_deleted == False,
            )
            .first()
        )

    def create_register(
        self,
        cash_register: CashRegister,
    ):
        self.db.add(cash_register)
        self.db.commit()
        self.db.refresh(cash_register)

        return cash_register

    def update_register(
        self,
        cash_register: CashRegister,
    ):
        self.db.commit()
        self.db.refresh(cash_register)

        return cash_register

    # =============================
    # CASH MOVEMENTS
    # =============================

    def create_movement(
        self,
        movement: CashMovement,
    ):
        self.db.add(movement)
        self.db.commit()
        self.db.refresh(movement)

        return movement

    def get_movements(
        self,
        cash_register_id: int,
    ):
        return (
            self.db.query(CashMovement)
            .filter(
                CashMovement.cash_register_id == cash_register_id,
                CashMovement.is_deleted == False,
            )
            .order_by(CashMovement.id.desc())
            .all()
        )