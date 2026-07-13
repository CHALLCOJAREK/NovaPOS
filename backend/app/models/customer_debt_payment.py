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


class CustomerDebtPayment(Base):
    __tablename__ = "customer_debt_payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    customer_debt_id = Column(
        Integer,
        ForeignKey("customer_debts.id"),
        nullable=False,
        index=True
    )

    payment_method = Column(
        String(20),
        nullable=False
    )

    amount = Column(
        Numeric(10, 2),
        nullable=False
    )

    cash_register_id = Column(
        Integer,
        ForeignKey("cash_registers.id"),
        nullable=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    notes = Column(
        String(255),
        nullable=True
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

    debt = relationship(
        "CustomerDebt",
        back_populates="payments"
    )