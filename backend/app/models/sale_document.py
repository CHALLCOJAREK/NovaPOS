from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class SaleDocument(Base):
    __tablename__ = "sale_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    sale_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sales.id"),
        nullable=False,
        index=True,
    )

    document_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)

    serie: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    full_number: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
        index=True,
    )

    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    tax_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    whatsapp_sent: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
    )

    whatsapp_sent_at: Mapped[DateTime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
    )

    sale = relationship("Sale", back_populates="document")