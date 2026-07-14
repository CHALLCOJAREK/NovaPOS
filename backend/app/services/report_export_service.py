from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from sqlalchemy.orm import Session

from app.schemas.report_export import (
    ReportExportFormat,
    ReportExportResponse,
    ReportExportType,
)
from app.services.report_export_adapter import (
    ReportExportAdapter,
    ReportExportContext,
    ReportExportDataset,
    ReportSchema,
)
from app.services.report_service import ReportService
from app.services.store_setting_service import StoreSettingService
from app.utils.report_excel_generator import ReportExcelGenerator
from app.utils.report_export_config import ReportExportConfig
from app.utils.report_export_path import ReportExportPath
from app.utils.report_html_renderer import ReportHtmlRenderer
from app.utils.report_pdf_generator import ReportPdfGenerator


class ReportExportService:
    """
    Orquestador oficial de exportaciones profesionales de NovaPOS.

    Toda la información comercial proviene exclusivamente de ReportService.
    Este servicio no consulta repositorios ni ejecuta consultas SQL.
    """

    DOWNLOAD_ENDPOINT = "/api/v1/report-exports/download"

    def __init__(self, db: Session):
        self.db = db
        self.store_setting_service = StoreSettingService(db)

    def export_report(
        self,
        *,
        report_type: ReportExportType,
        export_format: ReportExportFormat,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> ReportExportResponse:
        """
        Genera un reporte PDF o Excel y retorna su información de descarga.
        """

        self._validate_request(
            report_type=report_type,
            export_format=export_format,
            start_date=start_date,
            end_date=end_date,
        )

        generated_at = datetime.now()

        report = self._get_report_data(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
        )

        dataset = ReportExportAdapter.adapt(
            report_type=report_type,
            report=report,
        )

        store = self._get_store_context()

        file_path = ReportExportPath.build_file_path(
            report_type=report_type,
            export_format=export_format,
            start_date=start_date,
            end_date=end_date,
            generated_at=generated_at,
        )

        try:
            if export_format == ReportExportFormat.PDF:
                generated_file = self._generate_pdf(
                    report_type=report_type,
                    report=report,
                    store=store,
                    generated_at=generated_at,
                    start_date=start_date,
                    end_date=end_date,
                    file_path=file_path,
                )
            elif export_format == ReportExportFormat.XLSX:
                generated_file = self._generate_excel(
                    report_type=report_type,
                    dataset=dataset,
                    generated_at=generated_at,
                    start_date=start_date,
                    end_date=end_date,
                    file_path=file_path,
                )
            else:
                raise ValueError(
                    "El formato de exportación solicitado no es válido."
                )

        except Exception:
            self._remove_incomplete_file(file_path)
            raise

        return self._build_response(
            report_type=report_type,
            export_format=export_format,
            generated_file=generated_file,
            generated_at=generated_at,
            start_date=start_date,
            end_date=end_date,
        )

    def _get_report_data(
        self,
        *,
        report_type: ReportExportType,
        start_date: date | None,
        end_date: date | None,
    ) -> ReportSchema:
        """
        Invoca exclusivamente los métodos públicos de ReportService.
        """

        if report_type == ReportExportType.SALES:
            return ReportService.get_sales_report(
                db=self.db,
                start_date=start_date,
                end_date=end_date,
            )

        if report_type == ReportExportType.PURCHASES:
            return ReportService.get_purchases_report(
                db=self.db,
                start_date=start_date,
                end_date=end_date,
            )

        if report_type == ReportExportType.INVENTORY:
            return ReportService.get_inventory_report(
                db=self.db,
            )

        if report_type == ReportExportType.CASH:
            return ReportService.get_cash_report(
                db=self.db,
                start_date=start_date,
                end_date=end_date,
            )

        if report_type == ReportExportType.CUSTOMERS:
            return ReportService.get_customers_report(
                db=self.db,
            )

        if report_type == ReportExportType.DEBTS:
            return ReportService.get_debts_report(
                db=self.db,
                start_date=start_date,
                end_date=end_date,
            )

        if report_type == ReportExportType.PRODUCTS:
            return ReportService.get_products_report(
                db=self.db,
            )

        if report_type == ReportExportType.SUPPLIERS:
            return ReportService.get_suppliers_report(
                db=self.db,
            )

        raise ValueError(
            f"Tipo de reporte no soportado: {report_type.value}"
        )

    def _get_store_context(self) -> dict[str, Any]:
        """
        Obtiene la configuración actual de tienda y prepara el logo Base64.
        """

        store_setting = self.store_setting_service.get_current()

        logo_path = getattr(
            store_setting,
            "logo_path",
            None,
        )

        return {
            "store_name": (
                getattr(store_setting, "store_name", None)
                or "Tienda de Abarrotes Danae"
            ),
            "business_name": getattr(
                store_setting,
                "business_name",
                None,
            ),
            "ruc": getattr(
                store_setting,
                "ruc",
                None,
            ),
            "address": getattr(
                store_setting,
                "address",
                None,
            ),
            "phone": getattr(
                store_setting,
                "phone",
                None,
            ),
            "whatsapp": getattr(
                store_setting,
                "whatsapp",
                None,
            ),
            "email": getattr(
                store_setting,
                "email",
                None,
            ),
            "logo_uri": StoreSettingService.get_logo_uri(
                logo_path,
            ),
        }

    def _generate_pdf(
        self,
        *,
        report_type: ReportExportType,
        report: ReportSchema,
        store: dict[str, Any],
        generated_at: datetime,
        start_date: date | None,
        end_date: date | None,
        file_path: Path,
    ) -> Path:
        """
        Construye el contexto HTML y genera el PDF mediante Playwright.
        """

        definition = ReportExportConfig.get_definition(
            report_type,
        )

        context = ReportExportAdapter.build_context(
            report_type=report_type,
            report=report,
            store=store,
            generated_at=generated_at,
            start_date=start_date,
            end_date=end_date,
        )

        pdf_context = self._prepare_pdf_context(
            context,
        )

        html_content = ReportHtmlRenderer.render(
            pdf_context,
        )

        return ReportPdfGenerator.generate(
            html_content=html_content,
            file_path=file_path,
            orientation=definition.pdf_orientation,
        )

    def _generate_excel(
        self,
        *,
        report_type: ReportExportType,
        dataset: ReportExportDataset,
        generated_at: datetime,
        start_date: date | None,
        end_date: date | None,
        file_path: Path,
    ) -> Path:
        """
        Genera un archivo Excel a partir del dataset normalizado.
        """

        definition = ReportExportConfig.get_definition(
            report_type,
        )

        return ReportExcelGenerator.generate(
            file_path=file_path,
            report_title=definition.title,
            sheet_name=definition.sheet_name,
            columns=dataset["columns"],
            rows=dataset["rows"],
            summary=ReportExportAdapter.get_excel_summary(
                dataset,
            ),
            metadata=ReportExportAdapter.get_excel_metadata(
                generated_at=generated_at,
                start_date=start_date,
                end_date=end_date,
            ),
        )

    @classmethod
    def _prepare_pdf_context(
        cls,
        context: ReportExportContext,
    ) -> ReportExportContext:
        """
        Convierte valores tipados del dataset en textos aptos para HTML.

        Excel conserva los valores originales para poder ordenar, filtrar
        y realizar cálculos. PDF recibe valores ya formateados.
        """

        formatted_rows: list[dict[str, Any]] = []

        columns = context["columns"]

        for row in context["rows"]:
            formatted_row: dict[str, Any] = {}

            for column in columns:
                key = column["key"]
                value = row.get(key)
                column_format = str(
                    column.get("format", "")
                ).strip().lower()

                formatted_row[key] = cls._format_pdf_value(
                    value=value,
                    column_format=column_format,
                )

            formatted_rows.append(formatted_row)

        return ReportExportContext(
            report_title=context["report_title"],
            report_type=context["report_type"],
            generated_at=context["generated_at"],
            start_date=context["start_date"],
            end_date=context["end_date"],
            store=context["store"],
            summary=context["summary"],
            columns=context["columns"],
            rows=formatted_rows,
        )

    @staticmethod
    def _format_pdf_value(
        *,
        value: Any,
        column_format: str,
    ) -> str:
        """
        Formatea un valor individual para su presentación en PDF.
        """

        if value is None:
            return "-"

        if column_format in {
            "currency",
            "money",
        }:
            return ReportExportAdapter.format_currency(
                value,
            )

        if column_format in {
            "decimal",
            "quantity",
        }:
            return ReportExportAdapter.format_quantity(
                value,
            )

        if column_format in {
            "percentage",
            "percent",
        }:
            return ReportExportAdapter.format_percentage(
                value,
            )

        if column_format == "date":
            if isinstance(value, datetime):
                return (
                    ReportExportAdapter.format_date(value)
                    or "-"
                )

            if isinstance(value, date):
                return (
                    ReportExportAdapter.format_date(value)
                    or "-"
                )

            return ReportExportAdapter.format_nullable(
                value,
            )

        if column_format == "datetime":
            if isinstance(value, datetime):
                return ReportExportAdapter.format_datetime(
                    value,
                )

            if isinstance(value, date):
                return (
                    ReportExportAdapter.format_date(value)
                    or "-"
                )

            return ReportExportAdapter.format_nullable(
                value,
            )

        if column_format == "integer":
            try:
                return str(int(value))
            except (TypeError, ValueError):
                return ReportExportAdapter.format_nullable(
                    value,
                )

        return ReportExportAdapter.format_nullable(
            value,
        )

    @staticmethod
    def _validate_request(
        *,
        report_type: ReportExportType,
        export_format: ReportExportFormat,
        start_date: date | None,
        end_date: date | None,
    ) -> None:
        """
        Valida formato, tipo de reporte y período solicitado.
        """

        if not ReportExportConfig.is_supported(
            report_type,
        ):
            raise ValueError(
                f"El reporte {report_type.value} no está soportado."
            )

        if export_format not in {
            ReportExportFormat.PDF,
            ReportExportFormat.XLSX,
        }:
            raise ValueError(
                "El formato debe ser pdf o xlsx."
            )

        if (
            start_date is not None
            and end_date is not None
            and start_date > end_date
        ):
            raise ValueError(
                "La fecha inicial no puede ser mayor que la fecha final."
            )

        definition = ReportExportConfig.get_definition(
            report_type,
        )

        if (
            not definition.supports_date_range
            and (
                start_date is not None
                or end_date is not None
            )
        ):
            raise ValueError(
                f"El reporte {report_type.value} no admite "
                "filtros por fecha."
            )

    @classmethod
    def _build_response(
        cls,
        *,
        report_type: ReportExportType,
        export_format: ReportExportFormat,
        generated_file: Path,
        generated_at: datetime,
        start_date: date | None,
        end_date: date | None,
    ) -> ReportExportResponse:
        """
        Construye la respuesta estándar de exportación.
        """

        if not generated_file.exists():
            raise RuntimeError(
                "El archivo exportado no existe."
            )

        relative_path = ReportExportPath.get_relative_path(
            generated_file,
        )

        query_string = urlencode(
            {
                "path": relative_path,
            }
        )

        download_url = (
            f"{cls.DOWNLOAD_ENDPOINT}"
            f"?{query_string}"
        )

        return ReportExportResponse(
            report_type=report_type,
            format=export_format,
            filename=generated_file.name,
            relative_path=relative_path,
            download_url=download_url,
            mime_type=ReportExportPath.get_mime_type(
                export_format,
            ),
            size_bytes=generated_file.stat().st_size,
            generated_at=generated_at,
            start_date=start_date,
            end_date=end_date,
        )

    @staticmethod
    def _remove_incomplete_file(
        file_path: Path,
    ) -> None:
        """
        Elimina un archivo incompleto cuando falla la exportación.
        """

        if file_path.exists() and file_path.is_file():
            file_path.unlink(missing_ok=True)