# app/services/supplier_service.py

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.supplier_repository import SupplierRepository
from app.schemas.supplier import SupplierCreate, SupplierUpdate


class SupplierService:

    def __init__(self):
        self.repository = SupplierRepository()

    def get_all_suppliers(self, db: Session):
        return self.repository.get_all(db)

    def get_supplier_by_id(self, db: Session, supplier_id: int):
        supplier = self.repository.get_by_id(db, supplier_id)

        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proveedor no encontrado",
            )

        return supplier

    def create_supplier(self, db: Session, supplier_data: SupplierCreate):
        existing_name = self.repository.get_by_name(db, supplier_data.name)

        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un proveedor con este nombre",
            )

        if supplier_data.ruc:
            existing_ruc = self.repository.get_by_ruc(db, supplier_data.ruc)

            if existing_ruc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un proveedor con este RUC",
                )

        if supplier_data.email:
            existing_email = self.repository.get_by_email(db, str(supplier_data.email))

            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un proveedor con este correo",
                )

        return self.repository.create(db, supplier_data)

    def update_supplier(
        self,
        db: Session,
        supplier_id: int,
        supplier_data: SupplierUpdate,
    ):
        supplier = self.repository.get_by_id(db, supplier_id)

        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proveedor no encontrado",
            )

        if supplier_data.name and supplier_data.name != supplier.name:
            existing_name = self.repository.get_by_name(db, supplier_data.name)

            if existing_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un proveedor con este nombre",
                )

        if supplier_data.ruc and supplier_data.ruc != supplier.ruc:
            existing_ruc = self.repository.get_by_ruc(db, supplier_data.ruc)

            if existing_ruc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un proveedor con este RUC",
                )

        if supplier_data.email and str(supplier_data.email) != supplier.email:
            existing_email = self.repository.get_by_email(db, str(supplier_data.email))

            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un proveedor con este correo",
                )

        return self.repository.update(db, supplier, supplier_data)

    def delete_supplier(self, db: Session, supplier_id: int):
        supplier = self.repository.get_by_id(db, supplier_id)

        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proveedor no encontrado",
            )

        return self.repository.soft_delete(db, supplier)