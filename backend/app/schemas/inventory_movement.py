from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.inventory_movement import InventoryMovementType


class InventoryMovementBase(BaseModel):
    product_id: int = Field(..., gt=0)
    movement_type: InventoryMovementType
    quantity: Decimal = Field(..., gt=0, decimal_places=3)
    reason: str = Field(..., min_length=2, max_length=150)
    reference_type: Optional[str] = Field(default=None, max_length=50)
    reference_id: Optional[int] = Field(default=None, gt=0)
    user_id: Optional[int] = Field(default=None, gt=0)
    notes: Optional[str] = None


class InventoryMovementCreate(InventoryMovementBase):
    pass


class InventoryMovementResponse(InventoryMovementBase):
    id: int
    previous_stock: Decimal
    new_stock: Decimal
    is_deleted: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)