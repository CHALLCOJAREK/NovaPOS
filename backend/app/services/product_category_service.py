from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product_category import ProductCategory
from app.repositories.product_category_repository import ProductCategoryRepository
from app.schemas.product_category import (
    ProductCategoryCreate,
    ProductCategoryUpdate,
)


class ProductCategoryService:

    def __init__(self) -> None:
        self.repository = ProductCategoryRepository()

    def get_all(
        self,
        db: Session,
    ) -> list[ProductCategory]:
        return self.repository.get_all(db)

    def get_by_id(
        self,
        db: Session,
        category_id: int,
    ) -> ProductCategory:
        category = self.repository.get_by_id(db, category_id)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada",
            )

        return category

    def create(
        self,
        db: Session,
        category: ProductCategoryCreate,
    ) -> ProductCategory:
        existing_category = self.repository.get_by_name(
            db,
            category.name,
        )

        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una categoría con ese nombre",
            )

        return self.repository.create(db, category)

    def update(
        self,
        db: Session,
        category_id: int,
        category_update: ProductCategoryUpdate,
    ) -> ProductCategory:
        category = self.get_by_id(db, category_id)

        if category_update.name:
            existing_category = self.repository.get_by_name(
                db,
                category_update.name,
            )

            if existing_category and existing_category.id != category_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe una categoría con ese nombre",
                )

        return self.repository.update(
            db,
            category,
            category_update,
        )

    def soft_delete(
        self,
        db: Session,
        category_id: int,
    ) -> ProductCategory:
        category = self.get_by_id(db, category_id)

        return self.repository.soft_delete(
            db,
            category,
        )