from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    full_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    document_number: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True, index=True)
    whatsapp: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True, index=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    total_purchased: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_debt: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )
    sales = relationship(
        "Sale",
        back_populates="customer"
    )