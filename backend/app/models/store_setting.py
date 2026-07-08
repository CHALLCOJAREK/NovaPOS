from sqlalchemy import String, Boolean, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base import Base


class StoreSetting(Base):
    __tablename__ = "store_settings"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    store_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    business_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    ruc: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    address: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    whatsapp: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    email: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    logo_path: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="PEN",
        nullable=False
    )

    igv_percentage: Mapped[float] = mapped_column(
        Numeric(5, 2),
        default=18.00,
        nullable=False
    )

    receipt_footer: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        onupdate=datetime.utcnow
    )