from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.get(
    "/",
    response_model=list[ProductResponse],
    status_code=status.HTTP_200_OK,
)
def get_products(db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_products()


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.create_product(product_data)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
)
def get_product_by_id(
    product_id: int,
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.get_product_by_id(product_id)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.update_product(product_id, product_data)


@router.delete(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.delete_product(product_id)