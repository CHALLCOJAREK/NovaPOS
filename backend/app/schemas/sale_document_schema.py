from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SaleDocumentBase(BaseModel):
    sale_id: int = Field(gt=0)
    document_type: str = Field(min_length=1, max_length=30)
    serie: str = Field(min_length=1, max_length=10)
    number: int = Field(gt=0)
    full_number: str = Field(min_length=1, max_length=30)

    subtotal: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    tax_amount: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    total_amount: Decimal = Field(ge=0, max_digits=12, decimal_places=2)


class SaleDocumentCreate(SaleDocumentBase):
    pdf_path: str | None = Field(default=None, max_length=500)
    image_path: str | None = Field(default=None, max_length=500)


class SaleDocumentPathsUpdate(BaseModel):
    pdf_path: str | None = Field(default=None, max_length=500)
    image_path: str | None = Field(default=None, max_length=500)


class SaleDocumentResponse(SaleDocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pdf_path: str | None
    image_path: str | None
    whatsapp_sent: bool
    whatsapp_sent_at: datetime | None
    created_at: datetime
    is_deleted: bool


class SaleDocumentDownloadInfo(BaseModel):
    id: int
    sale_id: int
    document_type: str
    full_number: str
    pdf_path: str | None
    image_path: str | None
    pdf_available: bool
    image_available: bool