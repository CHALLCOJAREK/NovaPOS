from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id"),
        nullable=False,
        index=True,
    )

    document_type: Mapped[str] = mapped_column(String(30), nullable=False)
    document_number: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)

    purchase_date: Mapped[Date] = mapped_column(Date, nullable=False)

    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_source_path: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

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

    supplier = relationship("Supplier")
    items = relationship(
        "PurchaseItem",
        back_populates="purchase",
        cascade="all, delete-orphan",
    )