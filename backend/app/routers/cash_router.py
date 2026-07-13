from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.cash_register import (
    CashRegisterClose,
    CashRegisterOpen,
    CashRegisterResponse,
)
from app.schemas.cash_movement import (
    CashMovementCreate,
    CashMovementResponse,
)
from app.services.cash_service import CashService


router = APIRouter(
    prefix="/cash-registers",
    tags=["Cash Registers"],
)


@router.post(
    "/open",
    response_model=CashRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def open_cash_register(
    data: CashRegisterOpen,
    db: Session = Depends(get_db),
):
    service = CashService(db)
    return service.open_register(data)


@router.get(
    "/current",
    response_model=CashRegisterResponse,
)
def get_current_cash_register(
    db: Session = Depends(get_db),
):
    service = CashService(db)
    return service.get_current_register()


@router.get(
    "/",
    response_model=list[CashRegisterResponse],
)
def get_cash_registers(
    db: Session = Depends(get_db),
):
    service = CashService(db)
    return service.get_all_registers()


@router.get(
    "/{cash_register_id}",
    response_model=CashRegisterResponse,
)
def get_cash_register_by_id(
    cash_register_id: int,
    db: Session = Depends(get_db),
):
    service = CashService(db)
    return service.get_register_by_id(cash_register_id)


@router.post(
    "/{cash_register_id}/movements",
    response_model=CashMovementResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_cash_movement(
    cash_register_id: int,
    data: CashMovementCreate,
    db: Session = Depends(get_db),
):
    service = CashService(db)
    return service.create_manual_movement(cash_register_id, data)


@router.get(
    "/{cash_register_id}/movements",
    response_model=list[CashMovementResponse],
)
def get_cash_movements(
    cash_register_id: int,
    db: Session = Depends(get_db),
):
    service = CashService(db)
    return service.get_movements(cash_register_id)


@router.post(
    "/{cash_register_id}/close",
    response_model=CashRegisterResponse,
)
def close_cash_register(
    cash_register_id: int,
    data: CashRegisterClose,
    db: Session = Depends(get_db),
):
    service = CashService(db)
    return service.close_register(cash_register_id, data)