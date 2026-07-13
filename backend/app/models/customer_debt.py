from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric,
    String,
    Boolean,
    DateTime
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class CustomerDebt(Base):
    __tablename__ = "customer_debts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
        index=True
    )

    sale_id = Column(
        Integer,
        ForeignKey("sales.id"),
        nullable=False,
        unique=True,
        index=True
    )

    original_amount = Column(
        Numeric(10, 2),
        nullable=False
    )

    paid_amount = Column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    pending_amount = Column(
        Numeric(10, 2),
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False,
        default="PENDING"
    )

    is_deleted = Column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    customer = relationship(
        "Customer"
    )

    sale = relationship(
        "Sale"
    )

    payments = relationship(
        "CustomerDebtPayment",
        back_populates="debt"
    )