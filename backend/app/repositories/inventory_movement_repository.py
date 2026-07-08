from sqlalchemy.orm import Session

from app.models.inventory_movement import InventoryMovement
from app.schemas.inventory_movement import InventoryMovementCreate


class InventoryMovementRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[InventoryMovement]:
        return (
            self.db.query(InventoryMovement)
            .filter(InventoryMovement.is_deleted == False)
            .order_by(InventoryMovement.created_at.desc())
            .all()
        )

    def get_by_id(self, movement_id: int) -> InventoryMovement | None:
        return (
            self.db.query(InventoryMovement)
            .filter(
                InventoryMovement.id == movement_id,
                InventoryMovement.is_deleted == False,
            )
            .first()
        )

    def get_by_product_id(self, product_id: int) -> list[InventoryMovement]:
        return (
            self.db.query(InventoryMovement)
            .filter(
                InventoryMovement.product_id == product_id,
                InventoryMovement.is_deleted == False,
            )
            .order_by(InventoryMovement.created_at.desc())
            .all()
        )

    def create(
        self,
        movement_data: InventoryMovementCreate,
        previous_stock,
        new_stock,
    ) -> InventoryMovement:
        movement = InventoryMovement(
            **movement_data.model_dump(),
            previous_stock=previous_stock,
            new_stock=new_stock,
        )

        self.db.add(movement)
        self.db.commit()
        self.db.refresh(movement)

        return movement

    def soft_delete(self, movement: InventoryMovement) -> InventoryMovement:
        movement.is_deleted = True

        self.db.commit()
        self.db.refresh(movement)

        return movement