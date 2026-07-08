from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship
from app.db.base import Base


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    sale_id = Column(
        Integer,
        ForeignKey("sales.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    quantity = Column(
        Numeric(10, 3),
        nullable=False
    )

    unit_price = Column(
        Numeric(10, 2),
        nullable=False
    )

    unit_cost = Column(
        Numeric(10, 2),
        nullable=False
    )

    subtotal = Column(
        Numeric(10, 2),
        nullable=False
    )

    cost_total = Column(
        Numeric(10, 2),
        nullable=False
    )

    profit_amount = Column(
        Numeric(10, 2),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    sale = relationship(
        "Sale",
        back_populates="items"
    )

    product = relationship(
        "Product"
    )