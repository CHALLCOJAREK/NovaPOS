from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.inventory_movement import InventoryMovementType
from app.models.product import Product
from app.repositories.inventory_movement_repository import InventoryMovementRepository
from app.schemas.inventory_movement import InventoryMovementCreate


class InventoryMovementService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = InventoryMovementRepository(db)

    def get_all_movements(self):
        return self.repository.get_all()

    def get_movement_by_id(self, movement_id: int):
        movement = self.repository.get_by_id(movement_id)

        if not movement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movimiento de inventario no encontrado",
            )

        return movement

    def get_movements_by_product_id(self, product_id: int):
        product = self._get_active_product(product_id)
        return self.repository.get_by_product_id(product.id)

    def create_movement(self, movement_data: InventoryMovementCreate):
        product = self._get_active_product(movement_data.product_id)

        previous_stock = Decimal(product.stock)
        quantity = Decimal(movement_data.quantity)

        if movement_data.movement_type == InventoryMovementType.IN:
            new_stock = previous_stock + quantity

        elif movement_data.movement_type == InventoryMovementType.OUT:
            new_stock = previous_stock - quantity

            if new_stock < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Stock insuficiente para realizar la salida",
                )

        elif movement_data.movement_type == InventoryMovementType.ADJUSTMENT:
            new_stock = quantity

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de movimiento inválido",
            )

        product.stock = new_stock

        movement = self.repository.create(
            movement_data=movement_data,
            previous_stock=previous_stock,
            new_stock=new_stock,
        )

        return movement

    def soft_delete_movement(self, movement_id: int):
        movement = self.get_movement_by_id(movement_id)
        return self.repository.soft_delete(movement)

    def _get_active_product(self, product_id: int) -> Product:
        product = (
            self.db.query(Product)
            .filter(
                Product.id == product_id,
                Product.is_deleted == False,
            )
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )

        return product