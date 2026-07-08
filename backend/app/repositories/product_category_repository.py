from sqlalchemy.orm import Session

from app.models.product_category import ProductCategory
from app.schemas.product_category import (
    ProductCategoryCreate,
    ProductCategoryUpdate,
)


class ProductCategoryRepository:

    def get_all(
        self,
        db: Session,
    ) -> list[ProductCategory]:
        return (
            db.query(ProductCategory)
            .filter(ProductCategory.is_deleted == False)
            .all()
        )


    def get_by_id(
        self,
        db: Session,
        category_id: int,
    ) -> ProductCategory | None:
        return (
            db.query(ProductCategory)
            .filter(
                ProductCategory.id == category_id,
                ProductCategory.is_active == True,
                ProductCategory.is_deleted == False,
            )
            .first()
        )


    def get_by_name(
        self,
        db: Session,
        name: str,
    ) -> ProductCategory | None:
        return (
            db.query(ProductCategory)
            .filter(
                ProductCategory.name == name,
                ProductCategory.is_deleted == False,
            )
            .first()
        )


    def create(
        self,
        db: Session,
        category: ProductCategoryCreate,
    ) -> ProductCategory:

        db_category = ProductCategory(
            **category.model_dump()
        )

        db.add(db_category)
        db.commit()
        db.refresh(db_category)

        return db_category


    def update(
        self,
        db: Session,
        db_category: ProductCategory,
        category_update: ProductCategoryUpdate,
    ) -> ProductCategory:

        update_data = category_update.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(
                db_category,
                field,
                value,
            )

        db.commit()
        db.refresh(db_category)

        return db_category


    def soft_delete(
        self,
        db: Session,
        db_category: ProductCategory,
    ) -> ProductCategory:

        db_category.is_deleted = True
        db_category.is_active = False

        db.commit()
        db.refresh(db_category)

        return db_category
    
    