# app/repositories/supplier_repository.py

from sqlalchemy.orm import Session

from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate


class SupplierRepository:

    def get_all(self, db: Session):
        return (
            db.query(Supplier)
            .filter(Supplier.is_deleted == False)
            .order_by(Supplier.name.asc())
            .all()
        )

    def get_by_id(self, db: Session, supplier_id: int):
        return (
            db.query(Supplier)
            .filter(
                Supplier.id == supplier_id,
                Supplier.is_active == True,
                Supplier.is_deleted == False,
            )
            .first()
        )

    def get_by_name(self, db: Session, name: str):
        return (
            db.query(Supplier)
            .filter(
                Supplier.name == name,
                Supplier.is_deleted == False
            )
            .first()
        )

    def get_by_ruc(self, db: Session, ruc: str):
        return (
            db.query(Supplier)
            .filter(
                Supplier.ruc == ruc,
                Supplier.is_deleted == False
            )
            .first()
        )

    def get_by_email(self, db: Session, email: str):
        return (
            db.query(Supplier)
            .filter(
                Supplier.email == email,
                Supplier.is_deleted == False
            )
            .first()
        )

    def create(
        self,
        db: Session,
        supplier_data: SupplierCreate
    ):
        supplier = Supplier(
            **supplier_data.model_dump()
        )

        db.add(supplier)
        db.commit()
        db.refresh(supplier)

        return supplier

    def update(
        self,
        db: Session,
        supplier: Supplier,
        supplier_data: SupplierUpdate
    ):
        update_data = supplier_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(supplier, field, value)

        db.commit()
        db.refresh(supplier)

        return supplier

    def soft_delete(
        self,
        db: Session,
        supplier: Supplier
    ):
        supplier.is_deleted = True
        supplier.is_active = False

        db.commit()
        db.refresh(supplier)

        return supplier