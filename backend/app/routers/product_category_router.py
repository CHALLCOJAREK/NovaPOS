from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.product_category import (
    ProductCategoryCreate,
    ProductCategoryResponse,
    ProductCategoryUpdate,
)
from app.services.product_category_service import ProductCategoryService


router = APIRouter(
    prefix="/product-categories",
    tags=["Product Categories"],
)

service = ProductCategoryService()


@router.get(
    "/",
    response_model=list[ProductCategoryResponse],
)
def get_product_categories(
    db: Session = Depends(get_db),
):
    return service.get_all(db)


@router.post(
    "/",
    response_model=ProductCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product_category(
    category: ProductCategoryCreate,
    db: Session = Depends(get_db),
):
    return service.create(db, category)


@router.get(
    "/{category_id}",
    response_model=ProductCategoryResponse,
)
def get_product_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    return service.get_by_id(db, category_id)


@router.put(
    "/{category_id}",
    response_model=ProductCategoryResponse,
)
def update_product_category(
    category_id: int,
    category: ProductCategoryUpdate,
    db: Session = Depends(get_db),
):
    return service.update(db, category_id, category)


@router.delete(
    "/{category_id}",
    response_model=ProductCategoryResponse,
)
def delete_product_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    return service.soft_delete(db, category_id)

