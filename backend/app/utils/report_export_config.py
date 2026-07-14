from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, Mapping

from app.schemas.report_export import ReportExportType


@dataclass(frozen=True, slots=True)
class ReportExportDefinition:
    """
    Configuración visual y funcional de un reporte exportable.

    No contiene consultas, acceso a base de datos ni reglas comerciales.
    """

    report_type: ReportExportType
    title: str
    sheet_name: str
    display_code: str
    filename_prefix: str
    pdf_orientation: Literal["portrait", "landscape"]
    supports_date_range: bool


class ReportExportConfig:
    """
    Registro central de los reportes exportables de NovaPOS.

    Toda configuración es inmutable para evitar modificaciones accidentales
    durante la ejecución de la aplicación.
    """

    _DEFINITIONS: Mapping[
        ReportExportType,
        ReportExportDefinition,
    ] = MappingProxyType(
        {
            ReportExportType.SALES: ReportExportDefinition(
                report_type=ReportExportType.SALES,
                title="Reporte de Ventas",
                sheet_name="Ventas",
                display_code="VENTAS",
                filename_prefix="ventas",
                pdf_orientation="landscape",
                supports_date_range=True,
            ),
            ReportExportType.PURCHASES: ReportExportDefinition(
                report_type=ReportExportType.PURCHASES,
                title="Reporte de Compras",
                sheet_name="Compras",
                display_code="COMPRAS",
                filename_prefix="compras",
                pdf_orientation="landscape",
                supports_date_range=True,
            ),
            ReportExportType.INVENTORY: ReportExportDefinition(
                report_type=ReportExportType.INVENTORY,
                title="Reporte de Inventario",
                sheet_name="Inventario",
                display_code="INVENTARIO",
                filename_prefix="inventario",
                pdf_orientation="landscape",
                supports_date_range=False,
            ),
            ReportExportType.CASH: ReportExportDefinition(
                report_type=ReportExportType.CASH,
                title="Reporte de Caja",
                sheet_name="Caja",
                display_code="CAJA",
                filename_prefix="caja",
                pdf_orientation="landscape",
                supports_date_range=True,
            ),
            ReportExportType.CUSTOMERS: ReportExportDefinition(
                report_type=ReportExportType.CUSTOMERS,
                title="Reporte de Clientes",
                sheet_name="Clientes",
                display_code="CLIENTES",
                filename_prefix="clientes",
                pdf_orientation="landscape",
                supports_date_range=False,
            ),
            ReportExportType.DEBTS: ReportExportDefinition(
                report_type=ReportExportType.DEBTS,
                title="Reporte de Fiados",
                sheet_name="Fiados",
                display_code="FIADOS",
                filename_prefix="fiados",
                pdf_orientation="landscape",
                supports_date_range=True,
            ),
            ReportExportType.PRODUCTS: ReportExportDefinition(
                report_type=ReportExportType.PRODUCTS,
                title="Reporte de Productos",
                sheet_name="Productos",
                display_code="PRODUCTOS",
                filename_prefix="productos",
                pdf_orientation="landscape",
                supports_date_range=False,
            ),
            ReportExportType.SUPPLIERS: ReportExportDefinition(
                report_type=ReportExportType.SUPPLIERS,
                title="Reporte de Proveedores",
                sheet_name="Proveedores",
                display_code="PROVEEDORES",
                filename_prefix="proveedores",
                pdf_orientation="landscape",
                supports_date_range=False,
            ),
        }
    )

    @classmethod
    def get_definition(
        cls,
        report_type: ReportExportType,
    ) -> ReportExportDefinition:
        """
        Retorna la configuración oficial del reporte solicitado.
        """

        try:
            return cls._DEFINITIONS[report_type]
        except KeyError as exc:
            raise ValueError(
                f"Tipo de reporte no configurado: {report_type}"
            ) from exc

    @classmethod
    def get_all_definitions(
        cls,
    ) -> tuple[ReportExportDefinition, ...]:
        """
        Retorna todas las configuraciones registradas.
        """

        return tuple(cls._DEFINITIONS.values())

    @classmethod
    def is_supported(
        cls,
        report_type: ReportExportType,
    ) -> bool:
        """
        Indica si un tipo de reporte tiene configuración de exportación.
        """

        return report_type in cls._DEFINITIONS

    @classmethod
    def validate(cls) -> bool:
        """
        Verifica la integridad de toda la configuración.
        """

        expected_report_types = set(ReportExportType)
        configured_report_types = set(cls._DEFINITIONS)

        missing_report_types = (
            expected_report_types - configured_report_types
        )

        unexpected_report_types = (
            configured_report_types - expected_report_types
        )

        if missing_report_types:
            missing_values = ", ".join(
                sorted(
                    report_type.value
                    for report_type in missing_report_types
                )
            )

            raise RuntimeError(
                "Faltan configuraciones para los reportes: "
                f"{missing_values}"
            )

        if unexpected_report_types:
            unexpected_values = ", ".join(
                sorted(
                    report_type.value
                    for report_type in unexpected_report_types
                )
            )

            raise RuntimeError(
                "Existen configuraciones inesperadas: "
                f"{unexpected_values}"
            )

        sheet_names: set[str] = set()
        filename_prefixes: set[str] = set()
        display_codes: set[str] = set()

        for report_type, definition in cls._DEFINITIONS.items():
            cls._validate_definition(
                report_type=report_type,
                definition=definition,
            )

            normalized_sheet_name = (
                definition.sheet_name.strip().lower()
            )

            normalized_filename_prefix = (
                definition.filename_prefix.strip().lower()
            )

            normalized_display_code = (
                definition.display_code.strip().upper()
            )

            if normalized_sheet_name in sheet_names:
                raise RuntimeError(
                    "Existe un nombre de hoja Excel duplicado: "
                    f"{definition.sheet_name}"
                )

            if normalized_filename_prefix in filename_prefixes:
                raise RuntimeError(
                    "Existe un prefijo de archivo duplicado: "
                    f"{definition.filename_prefix}"
                )

            if normalized_display_code in display_codes:
                raise RuntimeError(
                    "Existe un código visual duplicado: "
                    f"{definition.display_code}"
                )

            sheet_names.add(normalized_sheet_name)
            filename_prefixes.add(normalized_filename_prefix)
            display_codes.add(normalized_display_code)

        return True

    @staticmethod
    def _validate_definition(
        *,
        report_type: ReportExportType,
        definition: ReportExportDefinition,
    ) -> None:
        """
        Valida una configuración individual.
        """

        if definition.report_type != report_type:
            raise RuntimeError(
                "El tipo registrado no coincide con la definición: "
                f"{report_type.value}"
            )

        if not definition.title.strip():
            raise RuntimeError(
                f"El reporte {report_type.value} no tiene título."
            )

        if not definition.sheet_name.strip():
            raise RuntimeError(
                f"El reporte {report_type.value} no tiene hoja Excel."
            )

        if len(definition.sheet_name) > 31:
            raise RuntimeError(
                "El nombre de hoja Excel excede los 31 caracteres: "
                f"{definition.sheet_name}"
            )

        if not definition.display_code.strip():
            raise RuntimeError(
                f"El reporte {report_type.value} no tiene código visual."
            )

        if not definition.filename_prefix.strip():
            raise RuntimeError(
                f"El reporte {report_type.value} no tiene prefijo."
            )

        if definition.pdf_orientation not in {
            "portrait",
            "landscape",
        }:
            raise RuntimeError(
                "La orientación PDF configurada no es válida para "
                f"{report_type.value}."
            )