from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Product]:
        return (
            self.db.query(Product)
            .filter(Product.is_deleted == False)
            .order_by(Product.id.desc())
            .all()
        )

    def get_by_id(self, product_id: int) -> Product | None:
        return (
            self.db.query(Product)
            .filter(
                Product.id == product_id,
                Product.is_deleted == False,
                Product.is_active == True,
            )
            .first()
        )

    def get_by_internal_code(self, internal_code: str) -> Product | None:
        return (
            self.db.query(Product)
            .filter(
                Product.internal_code == internal_code,
                Product.is_deleted == False,
            )
            .first()
        )

    def get_by_barcode(self, barcode: str) -> Product | None:
        return (
            self.db.query(Product)
            .filter(
                Product.barcode == barcode,
                Product.is_deleted == False,
            )
            .first()
        )

    def get_by_name_and_brand(self, name: str, brand: str | None) -> Product | None:
        return (
            self.db.query(Product)
            .filter(
                and_(
                    Product.name == name,
                    Product.brand == brand,
                    Product.is_deleted == False,
                )
            )
            .first()
        )

    def get_by_internal_code_excluding_id(
        self,
        internal_code: str,
        product_id: int,
    ) -> Product | None:
        return (
            self.db.query(Product)
            .filter(
                Product.internal_code == internal_code,
                Product.id != product_id,
                Product.is_deleted == False,
            )
            .first()
        )

    def get_by_barcode_excluding_id(
        self,
        barcode: str,
        product_id: int,
    ) -> Product | None:
        return (
            self.db.query(Product)
            .filter(
                Product.barcode == barcode,
                Product.id != product_id,
                Product.is_deleted == False,
            )
            .first()
        )

    def get_by_name_and_brand_excluding_id(
        self,
        name: str,
        brand: str | None,
        product_id: int,
    ) -> Product | None:
        return (
            self.db.query(Product)
            .filter(
                and_(
                    Product.name == name,
                    Product.brand == brand,
                    Product.id != product_id,
                    Product.is_deleted == False,
                )
            )
            .first()
        )

    def create(self, product_data: ProductCreate) -> Product:
        product = Product(**product_data.model_dump())

        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)

        return product

    def update(self, product: Product, product_data: ProductUpdate) -> Product:
        update_data = product_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(product, field, value)

        self.db.commit()
        self.db.refresh(product)

        return product

    def soft_delete(self, product: Product) -> Product:
        product.is_active = False
        product.is_deleted = True

        self.db.commit()
        self.db.refresh(product)

        return product