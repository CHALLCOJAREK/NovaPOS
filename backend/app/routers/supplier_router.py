# app/routers/supplier_router.py

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.supplier import SupplierCreate, SupplierResponse, SupplierUpdate
from app.services.supplier_service import SupplierService


router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"],
)

supplier_service = SupplierService()


@router.get("/", response_model=List[SupplierResponse])
def get_suppliers(db: Session = Depends(get_db)):
    return supplier_service.get_all_suppliers(db)


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
):
    return supplier_service.get_supplier_by_id(db, supplier_id)


@router.post(
    "/",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db),
):
    return supplier_service.create_supplier(db, supplier_data)


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db),
):
    return supplier_service.update_supplier(db, supplier_id, supplier_data)


@router.delete("/{supplier_id}", response_model=SupplierResponse)
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
):
    return supplier_service.delete_supplier(db, supplier_id)