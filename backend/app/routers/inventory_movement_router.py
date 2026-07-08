from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.inventory_movement import (
    InventoryMovementCreate,
    InventoryMovementResponse,
)
from app.services.inventory_movement_service import InventoryMovementService

router = APIRouter(
    prefix="/inventory-movements",
    tags=["Inventory Movements"],
)


@router.get("/", response_model=list[InventoryMovementResponse])
def get_inventory_movements(db: Session = Depends(get_db)):
    service = InventoryMovementService(db)
    return service.get_all_movements()


@router.post(
    "/",
    response_model=InventoryMovementResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_inventory_movement(
    movement_data: InventoryMovementCreate,
    db: Session = Depends(get_db),
):
    service = InventoryMovementService(db)
    return service.create_movement(movement_data)


@router.get("/{movement_id}", response_model=InventoryMovementResponse)
def get_inventory_movement(
    movement_id: int,
    db: Session = Depends(get_db),
):
    service = InventoryMovementService(db)
    return service.get_movement_by_id(movement_id)


@router.get(
    "/product/{product_id}",
    response_model=list[InventoryMovementResponse],
)
def get_inventory_movements_by_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    service = InventoryMovementService(db)
    return service.get_movements_by_product_id(product_id)


@router.delete("/{movement_id}", response_model=InventoryMovementResponse)
def delete_inventory_movement(
    movement_id: int,
    db: Session = Depends(get_db),
):
    service = InventoryMovementService(db)
    return service.soft_delete_movement(movement_id)