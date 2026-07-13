from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.cash_register import CashRegister
from app.models.cash_movement import CashMovement
from app.repositories.cash_repository import CashRepository
from app.schemas.cash_register import CashRegisterOpen, CashRegisterClose
from app.schemas.cash_movement import CashMovementCreate


class CashService:

    def __init__(self, db: Session):
        self.repository = CashRepository(db)

    def open_register(
        self,
        data: CashRegisterOpen,
    ):
        current_register = self.repository.get_open_register()

        if current_register:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una caja abierta",
            )

        cash_register = CashRegister(
            opened_by_user_id=data.opened_by_user_id,
            opening_amount=data.opening_amount,
            expected_cash_amount=data.opening_amount,
            notes=data.notes,
            status="OPEN",
        )

        created_register = self.repository.create_register(cash_register)

        opening_movement = CashMovement(
            cash_register_id=created_register.id,
            movement_type="OPENING",
            payment_method="CASH",
            amount=data.opening_amount,
            reason="Apertura de caja",
            reference_type="CASH_REGISTER",
            reference_id=created_register.id,
            user_id=data.opened_by_user_id,
            notes=data.notes,
        )

        self.repository.create_movement(opening_movement)

        return created_register

    def get_current_register(self):
        current_register = self.repository.get_open_register()

        if not current_register:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe una caja abierta",
            )

        return current_register

    def get_all_registers(self):
        return self.repository.get_all_registers()

    def get_register_by_id(
        self,
        cash_register_id: int,
    ):
        cash_register = self.repository.get_register_by_id(cash_register_id)

        if not cash_register:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Caja no encontrada",
            )

        return cash_register

    def create_manual_movement(
        self,
        cash_register_id: int,
        data: CashMovementCreate,
    ):
        cash_register = self.repository.get_register_by_id(cash_register_id)

        if not cash_register:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Caja no encontrada",
            )

        if cash_register.status != "OPEN":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pueden registrar movimientos en una caja cerrada",
            )

        amount = Decimal(data.amount)

        movement = CashMovement(
            cash_register_id=cash_register.id,
            movement_type=data.movement_type,
            payment_method=data.payment_method,
            amount=amount,
            reason=data.reason,
            reference_type="MANUAL",
            reference_id=None,
            user_id=data.user_id,
            notes=data.notes,
        )

        if data.movement_type == "MANUAL_INCOME":
            if data.payment_method == "CASH":
                cash_register.manual_income_amount += amount
                cash_register.expected_cash_amount += amount

            if data.payment_method == "YAPE":
                cash_register.manual_income_amount += amount
                cash_register.expected_yape_amount += amount

        elif data.movement_type == "MANUAL_EXPENSE":
            if data.payment_method != "CASH":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Los egresos manuales solo pueden registrarse en efectivo",
                )

            cash_register.manual_expense_amount += amount
            cash_register.expected_cash_amount -= amount

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de movimiento no válido",
            )

        self.repository.update_register(cash_register)
        return self.repository.create_movement(movement)

    def register_sale_payment(
        self,
        sale_id: int,
        payment_method: str,
        total_amount: Decimal,
        profit_amount: Decimal,
    ):
        cash_register = self.repository.get_open_register()

        if payment_method in ["CASH", "YAPE"] and not cash_register:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe existir una caja abierta para registrar esta venta",
            )

        if cash_register:

            if payment_method == "CASH":
                cash_register.cash_sales_amount += total_amount
                cash_register.expected_cash_amount += total_amount

            elif payment_method == "YAPE":
                cash_register.yape_sales_amount += total_amount
                cash_register.expected_yape_amount += total_amount

            elif payment_method == "CREDIT":
                cash_register.credit_sales_amount += total_amount

            cash_register.total_sales_amount += total_amount
            cash_register.total_profit_amount += profit_amount

            movement = CashMovement(
                cash_register_id=cash_register.id,
                movement_type="SALE",
                payment_method=payment_method,
                amount=total_amount,
                reason="Venta registrada",
                reference_type="SALE",
                reference_id=sale_id,
            )

            self.repository.update_register(cash_register)

            self.repository.create_movement(movement)

        return True

    def get_movements(
        self,
        cash_register_id: int,
    ):
        cash_register = self.repository.get_register_by_id(cash_register_id)

        if not cash_register:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Caja no encontrada",
            )

        return self.repository.get_movements(cash_register_id)

    def close_register(
        self,
        cash_register_id: int,
        data: CashRegisterClose,
    ):
        cash_register = self.repository.get_register_by_id(cash_register_id)

        if not cash_register:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Caja no encontrada",
            )

        if cash_register.status != "OPEN":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La caja ya está cerrada",
            )

        counted_cash = Decimal(data.counted_cash_amount)
        confirmed_yape = Decimal(data.confirmed_yape_amount)

        cash_register.counted_cash_amount = counted_cash
        cash_register.confirmed_yape_amount = confirmed_yape

        cash_register.cash_difference_amount = (
            counted_cash - cash_register.expected_cash_amount
        )
        cash_register.yape_difference_amount = (
            confirmed_yape - cash_register.expected_yape_amount
        )

        cash_register.closed_by_user_id = data.closed_by_user_id
        cash_register.close_notes = data.close_notes
        cash_register.closed_at = datetime.now(timezone.utc)
        cash_register.status = "CLOSED"

        self.repository.update_register(cash_register)

        closing_movement = CashMovement(
            cash_register_id=cash_register.id,
            movement_type="CLOSING_ADJUSTMENT",
            payment_method="CASH",
            amount=cash_register.cash_difference_amount,
            reason="Cierre de caja",
            reference_type="CASH_REGISTER",
            reference_id=cash_register.id,
            user_id=data.closed_by_user_id,
            notes=data.close_notes,
        )

        self.repository.create_movement(closing_movement)

        return cash_register