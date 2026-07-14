from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ReportExportFormat(str, Enum):
    PDF = "pdf"
    XLSX = "xlsx"


class ReportExportType(str, Enum):
    SALES = "sales"
    PURCHASES = "purchases"
    INVENTORY = "inventory"
    CASH = "cash"
    CUSTOMERS = "customers"
    DEBTS = "debts"
    PRODUCTS = "products"
    SUPPLIERS = "suppliers"


class ReportExportFilters(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    start_date: date | None = Field(
        default=None,
        description="Fecha inicial opcional utilizada para filtrar el reporte.",
    )
    end_date: date | None = Field(
        default=None,
        description="Fecha final opcional utilizada para filtrar el reporte.",
    )


class ReportExportResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid",
    )

    report_type: ReportExportType = Field(
        description="Tipo de reporte exportado.",
    )
    format: ReportExportFormat = Field(
        description="Formato del archivo generado.",
    )
    filename: str = Field(
        min_length=1,
        max_length=255,
        description="Nombre físico del archivo generado.",
    )
    relative_path: str = Field(
        min_length=1,
        description="Ruta relativa almacenada dentro del directorio de uploads.",
    )
    download_url: str = Field(
        min_length=1,
        description="URL REST utilizada para descargar el archivo.",
    )
    mime_type: str = Field(
        min_length=1,
        max_length=150,
        description="Tipo MIME correspondiente al archivo generado.",
    )
    size_bytes: int = Field(
        ge=0,
        description="Tamaño del archivo generado expresado en bytes.",
    )
    generated_at: datetime = Field(
        description="Fecha y hora en la que se generó el archivo.",
    )
    start_date: date | None = Field(
        default=None,
        description="Fecha inicial aplicada al reporte.",
    )
    end_date: date | None = Field(
        default=None,
        description="Fecha final aplicada al reporte.",
    )


class ReportExportDownloadInfo(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    filename: str = Field(
        min_length=1,
        max_length=255,
        description="Nombre del archivo solicitado.",
    )
    relative_path: str = Field(
        min_length=1,
        description="Ruta relativa validada del archivo.",
    )
    mime_type: str = Field(
        min_length=1,
        max_length=150,
        description="Tipo MIME del archivo solicitado.",
    )