from datetime import date
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.report_export import (
    ReportExportFormat,
    ReportExportResponse,
    ReportExportType,
)
from app.services.report_export_service import ReportExportService
from app.utils.report_export_path import ReportExportPath


router = APIRouter(
    prefix="/report-exports",
    tags=["Report Exports"],
)


def _export_report(
    *,
    report_type: ReportExportType,
    export_format: ReportExportFormat,
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
) -> ReportExportResponse:
    """
    Delega la exportación al servicio oficial y normaliza errores HTTP.
    """

    try:
        return ReportExportService(db).export_report(
            report_type=report_type,
            export_format=export_format,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    except OSError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible guardar el archivo exportado.",
        ) from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error


@router.get(
    "/sales",
    response_model=ReportExportResponse,
    summary="Exportar reporte de ventas",
)
def export_sales_report(
    export_format: ReportExportFormat = Query(
        alias="format",
        description="Formato del reporte: pdf o xlsx.",
    ),
    start_date: date | None = Query(
        default=None,
        description="Fecha inicial del reporte.",
    ),
    end_date: date | None = Query(
        default=None,
        description="Fecha final del reporte.",
    ),
    db: Session = Depends(get_db),
) -> ReportExportResponse:
    return _export_report(
        report_type=ReportExportType.SALES,
        export_format=export_format,
        start_date=start_date,
        end_date=end_date,
        db=db,
    )


@router.get(
    "/purchases",
    response_model=ReportExportResponse,
    summary="Exportar reporte de compras",
)
def export_purchases_report(
    export_format: ReportExportFormat = Query(
        alias="format",
        description="Formato del reporte: pdf o xlsx.",
    ),
    start_date: date | None = Query(
        default=None,
        description="Fecha inicial del reporte.",
    ),
    end_date: date | None = Query(
        default=None,
        description="Fecha final del reporte.",
    ),
    db: Session = Depends(get_db),
) -> ReportExportResponse:
    return _export_report(
        report_type=ReportExportType.PURCHASES,
        export_format=export_format,
        start_date=start_date,
        end_date=end_date,
        db=db,
    )


@router.get(
    "/inventory",
    response_model=ReportExportResponse,
    summary="Exportar reporte de inventario",
)
def export_inventory_report(
    export_format: ReportExportFormat = Query(
        alias="format",
        description="Formato del reporte: pdf o xlsx.",
    ),
    db: Session = Depends(get_db),
) -> ReportExportResponse:
    return _export_report(
        report_type=ReportExportType.INVENTORY,
        export_format=export_format,
        db=db,
    )


@router.get(
    "/cash",
    response_model=ReportExportResponse,
    summary="Exportar reporte de caja",
)
def export_cash_report(
    export_format: ReportExportFormat = Query(
        alias="format",
        description="Formato del reporte: pdf o xlsx.",
    ),
    start_date: date | None = Query(
        default=None,
        description="Fecha inicial del reporte.",
    ),
    end_date: date | None = Query(
        default=None,
        description="Fecha final del reporte.",
    ),
    db: Session = Depends(get_db),
) -> ReportExportResponse:
    return _export_report(
        report_type=ReportExportType.CASH,
        export_format=export_format,
        start_date=start_date,
        end_date=end_date,
        db=db,
    )


@router.get(
    "/customers",
    response_model=ReportExportResponse,
    summary="Exportar reporte de clientes",
)
def export_customers_report(
    export_format: ReportExportFormat = Query(
        alias="format",
        description="Formato del reporte: pdf o xlsx.",
    ),
    db: Session = Depends(get_db),
) -> ReportExportResponse:
    return _export_report(
        report_type=ReportExportType.CUSTOMERS,
        export_format=export_format,
        db=db,
    )


@router.get(
    "/debts",
    response_model=ReportExportResponse,
    summary="Exportar reporte de fiados",
)
def export_debts_report(
    export_format: ReportExportFormat = Query(
        alias="format",
        description="Formato del reporte: pdf o xlsx.",
    ),
    start_date: date | None = Query(
        default=None,
        description="Fecha inicial del reporte.",
    ),
    end_date: date | None = Query(
        default=None,
        description="Fecha final del reporte.",
    ),
    db: Session = Depends(get_db),
) -> ReportExportResponse:
    return _export_report(
        report_type=ReportExportType.DEBTS,
        export_format=export_format,
        start_date=start_date,
        end_date=end_date,
        db=db,
    )


@router.get(
    "/products",
    response_model=ReportExportResponse,
    summary="Exportar reporte de productos",
)
def export_products_report(
    export_format: ReportExportFormat = Query(
        alias="format",
        description="Formato del reporte: pdf o xlsx.",
    ),
    db: Session = Depends(get_db),
) -> ReportExportResponse:
    return _export_report(
        report_type=ReportExportType.PRODUCTS,
        export_format=export_format,
        db=db,
    )


@router.get(
    "/suppliers",
    response_model=ReportExportResponse,
    summary="Exportar reporte de proveedores",
)
def export_suppliers_report(
    export_format: ReportExportFormat = Query(
        alias="format",
        description="Formato del reporte: pdf o xlsx.",
    ),
    db: Session = Depends(get_db),
) -> ReportExportResponse:
    return _export_report(
        report_type=ReportExportType.SUPPLIERS,
        export_format=export_format,
        db=db,
    )


@router.get(
    "/download",
    response_class=FileResponse,
    summary="Descargar reporte exportado",
)
def download_report(
    path: str = Query(
        min_length=1,
        description=(
            "Ruta relativa devuelta por el endpoint de exportación."
        ),
    ),
) -> FileResponse:
    try:
        file_path = ReportExportPath.resolve_download_path(
            path,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El archivo de reporte solicitado no existe.",
        )

    export_format = _get_format_from_file(
        file_path,
    )

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type=ReportExportPath.get_mime_type(
            export_format,
        ),
    )


def _get_format_from_file(
    file_path: Path,
) -> ReportExportFormat:
    """
    Determina el formato del archivo validado para su descarga.
    """

    extension = file_path.suffix.lower()

    if extension == ".pdf":
        return ReportExportFormat.PDF

    if extension == ".xlsx":
        return ReportExportFormat.XLSX

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="El formato del archivo solicitado no está permitido.",
    )