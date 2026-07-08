from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.product_category_repository import ProductCategoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.supplier_repository import SupplierRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ProductRepository(db)
        self.category_repository = ProductCategoryRepository()
        self.supplier_repository = SupplierRepository()

    def get_products(self):
        return self.repository.get_all()

    def get_product_by_id(self, product_id: int):
        product = self.repository.get_by_id(product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )

        return product

    def create_product(self, product_data: ProductCreate):
        category = self.category_repository.get_by_id(
            self.db,
            product_data.category_id,
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoría no encontrada",
            )

        if product_data.supplier_id:
            supplier = self.supplier_repository.get_by_id(
                self.db,
                product_data.supplier_id,
            )

            if not supplier:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Proveedor no encontrado",
                )

        if product_data.internal_code:
            existing = self.repository.get_by_internal_code(product_data.internal_code)

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un producto con ese código interno",
                )

        if product_data.barcode:
            existing = self.repository.get_by_barcode(product_data.barcode)

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un producto con ese código de barras",
                )

        existing = self.repository.get_by_name_and_brand(
            product_data.name,
            product_data.brand,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un producto con ese nombre y marca",
            )

        return self.repository.create(product_data)

    def update_product(
        self,
        product_id: int,
        product_data: ProductUpdate,
    ):
        product = self.get_product_by_id(product_id)

        if product_data.category_id is not None:
            category = self.category_repository.get_by_id(
                self.db,
                product_data.category_id,
            )

            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Categoría no encontrada",
                )

        if product_data.supplier_id is not None:
            supplier = self.supplier_repository.get_by_id(
                self.db,
                product_data.supplier_id,
            )

            if not supplier:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Proveedor no encontrado",
                )

        if product_data.internal_code:
            existing = self.repository.get_by_internal_code_excluding_id(
                product_data.internal_code,
                product_id,
            )

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un producto con ese código interno",
                )

        if product_data.barcode:
            existing = self.repository.get_by_barcode_excluding_id(
                product_data.barcode,
                product_id,
            )

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un producto con ese código de barras",
                )

        new_name = product_data.name if product_data.name is not None else product.name
        new_brand = product_data.brand if product_data.brand is not None else product.brand

        existing = self.repository.get_by_name_and_brand_excluding_id(
            new_name,
            new_brand,
            product_id,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un producto con ese nombre y marca",
            )

        return self.repository.update(
            product,
            product_data,
        )

    def delete_product(self, product_id: int):
        product = self.get_product_by_id(product_id)

        return self.repository.soft_delete(product)