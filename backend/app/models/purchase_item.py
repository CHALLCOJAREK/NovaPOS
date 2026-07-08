from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    purchase_id: Mapped[int] = mapped_column(
        ForeignKey("purchases.id"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )

    package_total_cost: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    unit_quantity: Mapped[float] = mapped_column(
        Numeric(10, 3),
        nullable=False,
    )

    unit_cost: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    previous_cost: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    new_cost: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    previous_stock: Mapped[float] = mapped_column(
        Numeric(10, 3),
        nullable=False,
    )

    new_stock: Mapped[float] = mapped_column(
        Numeric(10, 3),
        nullable=False,
    )

    expiration_date: Mapped[Date | None] = mapped_column(
        Date,
        nullable=True,
    )

    batch: Mapped[str | None] = mapped_column(
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[DateTime | None] = mapped_column(
        DateTime,
        onupdate=func.now(),
        nullable=True,
    )


    purchase = relationship(
        "Purchase",
        back_populates="items",
    )

    product = relationship(
        "Product",
    )