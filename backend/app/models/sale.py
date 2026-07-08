from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=True
    )

    document_type = Column(
        String(50),
        nullable=False
    )

    payment_method = Column(
        String(50),
        nullable=False
    )

    subtotal = Column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    discount_amount = Column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    total_amount = Column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    total_cost = Column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    profit_amount = Column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    notes = Column(
        String(255),
        nullable=True
    )

    is_confirmed = Column(
        Boolean,
        nullable=False,
        default=True
    )

    is_deleted = Column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


    customer = relationship(
        "Customer",
        back_populates="sales"
    )

    items = relationship(
        "SaleItem",
        back_populates="sale",
        cascade="all, delete-orphan"
    )