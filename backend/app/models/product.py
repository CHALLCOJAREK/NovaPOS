from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)

    internal_code: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=True,
    )
    barcode: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=True,
    )

    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("product_categories.id"),
        nullable=False,
        index=True,
    )
    supplier_id: Mapped[int | None] = mapped_column(
        ForeignKey("suppliers.id"),
        nullable=True,
        index=True,
    )

    cost_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
    )
    sale_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
    )
    profit_margin: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
    )
    profit_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
    )

    stock: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),
        nullable=False,
        default=0,
    )
    minimum_stock: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),
        nullable=False,
        default=0,
    )

    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    batch: Mapped[str | None] = mapped_column(String(100), nullable=True)

    is_weighted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_frozen: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ACTIVE")

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        onupdate=datetime.utcnow,
    )

    category = relationship("ProductCategory", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    inventory_movements = relationship(
        "InventoryMovement",
        back_populates="product",
    )

    sale_items = relationship(
        "SaleItem",
        back_populates="product"
    )