from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.schemas.report_export import ReportExportFormat, ReportExportType


class ReportExportPath:
    REPORTS_DIRECTORY = "reportes"
    PDF_DIRECTORY = "pdf"
    EXCEL_DIRECTORY = "excel"

    ALLOWED_EXTENSIONS = {
        ReportExportFormat.PDF: ".pdf",
        ReportExportFormat.XLSX: ".xlsx",
    }

    MIME_TYPES = {
        ReportExportFormat.PDF: "application/pdf",
        ReportExportFormat.XLSX: (
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    }

    @classmethod
    def get_upload_root(cls) -> Path:
        """
        Retorna la carpeta raíz oficial de archivos subidos.

        La ruta siempre proviene de settings.UPLOAD_PATH.
        """

        upload_root = Path(settings.UPLOAD_PATH).expanduser().resolve()
        upload_root.mkdir(parents=True, exist_ok=True)

        return upload_root

    @classmethod
    def get_reports_root(cls) -> Path:
        """
        Retorna la carpeta principal de reportes.
        """

        reports_root = cls.get_upload_root() / cls.REPORTS_DIRECTORY
        reports_root.mkdir(parents=True, exist_ok=True)

        return reports_root

    @classmethod
    def get_format_directory(
        cls,
        export_format: ReportExportFormat,
    ) -> Path:
        """
        Retorna y crea la carpeta correspondiente al formato solicitado.
        """

        if export_format == ReportExportFormat.PDF:
            directory_name = cls.PDF_DIRECTORY
        elif export_format == ReportExportFormat.XLSX:
            directory_name = cls.EXCEL_DIRECTORY
        else:
            raise ValueError(
                f"Formato de exportación no soportado: {export_format}"
            )

        format_directory = cls.get_reports_root() / directory_name
        format_directory.mkdir(parents=True, exist_ok=True)

        return format_directory

    @classmethod
    def build_filename(
        cls,
        report_type: ReportExportType,
        export_format: ReportExportFormat,
        start_date: date | None = None,
        end_date: date | None = None,
        generated_at: datetime | None = None,
    ) -> str:
        """
        Genera un nombre único y legible para el archivo exportado.

        Ejemplo:
        ventas_2026-07-01_2026-07-14_20260714_113045_a1b2c3d4.pdf
        """

        current_datetime = generated_at or datetime.now()
        extension = cls.get_extension(export_format)

        filename_parts = [
            cls._sanitize_filename_part(report_type.value),
        ]

        if start_date is not None:
            filename_parts.append(start_date.isoformat())

        if end_date is not None:
            filename_parts.append(end_date.isoformat())

        filename_parts.extend(
            [
                current_datetime.strftime("%Y%m%d_%H%M%S"),
                uuid4().hex[:8],
            ]
        )

        return "_".join(filename_parts) + extension

    @classmethod
    def build_file_path(
        cls,
        report_type: ReportExportType,
        export_format: ReportExportFormat,
        start_date: date | None = None,
        end_date: date | None = None,
        generated_at: datetime | None = None,
    ) -> Path:
        """
        Construye la ruta física completa de un nuevo reporte.
        """

        directory = cls.get_format_directory(export_format)

        filename = cls.build_filename(
            report_type=report_type,
            export_format=export_format,
            start_date=start_date,
            end_date=end_date,
            generated_at=generated_at,
        )

        return directory / filename

    @classmethod
    def get_relative_path(cls, file_path: Path | str) -> str:
        """
        Convierte una ruta física en una ruta relativa a UPLOAD_PATH.
        """

        upload_root = cls.get_upload_root()
        resolved_file_path = Path(file_path).expanduser().resolve()

        try:
            relative_path = resolved_file_path.relative_to(upload_root)
        except ValueError as exc:
            raise ValueError(
                "El archivo no pertenece al directorio oficial de uploads."
            ) from exc

        return relative_path.as_posix()

    @classmethod
    def resolve_download_path(cls, relative_path: str) -> Path:
        """
        Resuelve de forma segura una ruta relativa para descarga.

        Rechaza rutas externas y ataques de path traversal.
        """

        if not relative_path or not relative_path.strip():
            raise ValueError("La ruta del archivo es obligatoria.")

        upload_root = cls.get_upload_root()
        resolved_path = (upload_root / relative_path).resolve()

        try:
            resolved_path.relative_to(upload_root)
        except ValueError as exc:
            raise ValueError(
                "La ruta solicitada no pertenece al directorio de uploads."
            ) from exc

        reports_root = cls.get_reports_root()

        try:
            resolved_path.relative_to(reports_root)
        except ValueError as exc:
            raise ValueError(
                "La ruta solicitada no pertenece al directorio de reportes."
            ) from exc

        if resolved_path.suffix.lower() not in {".pdf", ".xlsx"}:
            raise ValueError(
                "El archivo solicitado no tiene una extensión permitida."
            )

        return resolved_path

    @classmethod
    def get_extension(
        cls,
        export_format: ReportExportFormat,
    ) -> str:
        """
        Retorna la extensión oficial del formato.
        """

        extension = cls.ALLOWED_EXTENSIONS.get(export_format)

        if extension is None:
            raise ValueError(
                f"Formato de exportación no soportado: {export_format}"
            )

        return extension

    @classmethod
    def get_mime_type(
        cls,
        export_format: ReportExportFormat,
    ) -> str:
        """
        Retorna el tipo MIME oficial del formato.
        """

        mime_type = cls.MIME_TYPES.get(export_format)

        if mime_type is None:
            raise ValueError(
                f"Formato de exportación no soportado: {export_format}"
            )

        return mime_type

    @staticmethod
    def _sanitize_filename_part(value: str) -> str:
        """
        Limpia una sección del nombre de archivo.
        """

        sanitized = value.strip().lower().replace(" ", "_")

        allowed_characters = {
            character
            for character in sanitized
            if character.isalnum() or character in {"_", "-"}
        }

        result = "".join(
            character
            for character in sanitized
            if character in allowed_characters
        )

        if not result:
            raise ValueError(
                "No fue posible construir un nombre de archivo válido."
            )

        return result