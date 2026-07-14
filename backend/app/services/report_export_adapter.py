from collections.abc import Callable, Mapping
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, TypedDict

from pydantic import BaseModel

from app.schemas.report import (
    CashReportSchema,
    CustomersReportSchema,
    DebtsReportSchema,
    InventoryReportSchema,
    ProductsReportSchema,
    PurchasesReportSchema,
    SalesReportSchema,
    SuppliersReportSchema,
)
from app.schemas.report_export import ReportExportType
from app.utils.report_export_config import ReportExportConfig


class ReportExportColumn(TypedDict, total=False):
    """
    Definición estándar de una columna exportable.
    """

    key: str
    label: str
    format: str
    alignment: str
    width: float


class ReportExportSummaryItem(TypedDict):
    """
    Indicador resumido utilizado en PDF.
    """

    label: str
    value: str


class ReportExportContext(TypedDict):
    """
    Contexto estándar consumido por PDF y Excel.
    """

    report_title: str
    report_type: str
    generated_at: str
    start_date: str | None
    end_date: str | None
    store: dict[str, Any]
    summary: list[ReportExportSummaryItem]
    columns: list[ReportExportColumn]
    rows: list[dict[str, Any]]


class ReportExportDataset(TypedDict):
    """
    Datos normalizados propios del reporte.

    El contexto final se completa posteriormente con información de tienda,
    fechas de generación y configuración visual.
    """

    summary: list[ReportExportSummaryItem]
    columns: list[ReportExportColumn]
    rows: list[dict[str, Any]]


ReportSchema = (
    SalesReportSchema
    | PurchasesReportSchema
    | InventoryReportSchema
    | CashReportSchema
    | CustomersReportSchema
    | DebtsReportSchema
    | ProductsReportSchema
    | SuppliersReportSchema
)


class ReportExportAdapter:
    """
    Adaptador de schemas comerciales a estructuras exportables.

    No consulta base de datos ni genera archivos. Su responsabilidad es
    convertir los schemas retornados por ReportService en datos estándar
    para ReportHtmlRenderer y ReportExcelGenerator.
    """

    REPORT_SCHEMA_TYPES: Mapping[
        ReportExportType,
        type[BaseModel],
    ] = {
        ReportExportType.SALES: SalesReportSchema,
        ReportExportType.PURCHASES: PurchasesReportSchema,
        ReportExportType.INVENTORY: InventoryReportSchema,
        ReportExportType.CASH: CashReportSchema,
        ReportExportType.CUSTOMERS: CustomersReportSchema,
        ReportExportType.DEBTS: DebtsReportSchema,
        ReportExportType.PRODUCTS: ProductsReportSchema,
        ReportExportType.SUPPLIERS: SuppliersReportSchema,
    }

    PAYMENT_METHOD_LABELS: Mapping[str, str] = {
        "CASH": "Efectivo",
        "YAPE": "Yape",
        "CREDIT": "Fiado",
    }

    DOCUMENT_TYPE_LABELS: Mapping[str, str] = {
        "BOLETA": "Boleta",
        "NOTA_VENTA": "Nota de Venta",
        "INVOICE": "Factura",
        "RECEIPT": "Boleta",
        "CREDIT_NOTE": "Nota de Crédito",
        "DEBIT_NOTE": "Nota de Débito",
    }

    STATUS_LABELS: Mapping[str, str] = {
        "ACTIVE": "Activo",
        "INACTIVE": "Inactivo",
        "OPEN": "Abierta",
        "CLOSED": "Cerrada",
        "PENDING": "Pendiente",
        "PARTIAL": "Parcial",
        "PAID": "Pagado",
        "CANCELLED": "Cancelado",
        "AVAILABLE": "Disponible",
        "OUT_OF_STOCK": "Sin stock",
        "LOW_STOCK": "Stock bajo",
        "EXPIRED": "Vencido",
    }

    @classmethod
    def adapt(
        cls,
        *,
        report_type: ReportExportType,
        report: ReportSchema,
    ) -> ReportExportDataset:
        """
        Convierte un schema de ReportService en un dataset estándar.

        El método valida primero que el schema recibido corresponda al tipo
        de reporte solicitado.
        """

        cls._validate_report_schema(
            report_type=report_type,
            report=report,
        )

        adapters: Mapping[
            ReportExportType,
            Callable[[Any], ReportExportDataset],
        ] = {
            ReportExportType.SALES: cls._adapt_sales,
            ReportExportType.PURCHASES: cls._adapt_purchases,
            ReportExportType.INVENTORY: cls._adapt_inventory,
            ReportExportType.CASH: cls._adapt_cash,
            ReportExportType.CUSTOMERS: cls._adapt_customers,
            ReportExportType.DEBTS: cls._adapt_debts,
            ReportExportType.PRODUCTS: cls._adapt_products,
            ReportExportType.SUPPLIERS: cls._adapt_suppliers,
        }

        adapter = adapters.get(report_type)

        if adapter is None:
            raise ValueError(
                f"No existe adaptador para el reporte: {report_type.value}"
            )

        dataset = adapter(report)

        cls._validate_dataset(dataset)

        return dataset

    @classmethod
    def build_context(
        cls,
        *,
        report_type: ReportExportType,
        report: ReportSchema,
        store: Mapping[str, Any],
        generated_at: datetime,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> ReportExportContext:
        """
        Construye el contexto completo utilizado por la plantilla PDF.

        La información de tienda debe llegar previamente procesada por el
        servicio responsable de configuración de la tienda.
        """

        cls._validate_period(
            start_date=start_date,
            end_date=end_date,
        )

        cls._validate_store(store)

        definition = ReportExportConfig.get_definition(
            report_type,
        )

        dataset = cls.adapt(
            report_type=report_type,
            report=report,
        )

        return ReportExportContext(
            report_title=definition.title,
            report_type=definition.display_code,
            generated_at=cls.format_datetime(generated_at),
            start_date=cls.format_date(start_date),
            end_date=cls.format_date(end_date),
            store=dict(store),
            summary=dataset["summary"],
            columns=dataset["columns"],
            rows=dataset["rows"],
        )

    @classmethod
    def get_excel_summary(
        cls,
        dataset: ReportExportDataset,
    ) -> dict[str, str]:
        """
        Convierte el resumen visual en un mapping apto para Excel.
        """

        cls._validate_dataset(dataset)

        return {
            item["label"]: item["value"]
            for item in dataset["summary"]
        }

    @classmethod
    def get_excel_metadata(
        cls,
        *,
        generated_at: datetime,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict[str, str]:
        """
        Construye metadatos generales para el archivo Excel.
        """

        cls._validate_period(
            start_date=start_date,
            end_date=end_date,
        )

        if start_date is not None and end_date is not None:
            period = (
                f"{cls.format_date(start_date)} "
                f"al {cls.format_date(end_date)}"
            )
        elif start_date is not None:
            period = f"Desde {cls.format_date(start_date)}"
        elif end_date is not None:
            period = f"Hasta {cls.format_date(end_date)}"
        else:
            period = "Periodo completo"

        return {
            "Periodo": period,
            "Generado": cls.format_datetime(generated_at),
            "Sistema": "NovaPOS",
        }

    @staticmethod
    def format_currency(
        value: Decimal | int | float | str | None,
    ) -> str:
        """
        Formatea importes monetarios en soles.
        """

        decimal_value = ReportExportAdapter._to_decimal(value)

        return f"S/ {decimal_value:,.2f}"

    @staticmethod
    def format_quantity(
        value: Decimal | int | float | str | None,
    ) -> str:
        """
        Formatea cantidades con tres decimales.
        """

        decimal_value = ReportExportAdapter._to_decimal(
            value,
            default="0.000",
        )

        return f"{decimal_value:,.3f}"

    @staticmethod
    def format_percentage(
        value: Decimal | int | float | str | None,
    ) -> str:
        """
        Formatea porcentajes comerciales.

        El valor se interpreta como porcentaje directo:
        18 equivale a 18.00 %.
        """

        decimal_value = ReportExportAdapter._to_decimal(value)

        return f"{decimal_value:,.2f} %"

    @staticmethod
    def format_date(
        value: date | datetime | None,
    ) -> str | None:
        """
        Formatea una fecha con convención peruana.
        """

        if value is None:
            return None

        if isinstance(value, datetime):
            value = value.date()

        return value.strftime("%d/%m/%Y")

    @staticmethod
    def format_datetime(
        value: datetime | None,
    ) -> str:
        """
        Formatea fecha y hora.
        """

        if value is None:
            return "-"

        return value.strftime("%d/%m/%Y %H:%M")

    @classmethod
    def format_payment_method(
        cls,
        value: str | Enum | None,
    ) -> str:
        """
        Traduce el método de pago interno a su etiqueta comercial.
        """

        normalized_value = cls._normalize_enum_or_string(value)

        if not normalized_value:
            return "-"

        return cls.PAYMENT_METHOD_LABELS.get(
            normalized_value,
            normalized_value.replace("_", " ").title(),
        )

    @classmethod
    def format_document_type(
        cls,
        value: str | Enum | None,
    ) -> str:
        """
        Traduce el tipo interno de documento.
        """

        normalized_value = cls._normalize_enum_or_string(value)

        if not normalized_value:
            return "-"

        return cls.DOCUMENT_TYPE_LABELS.get(
            normalized_value,
            normalized_value.replace("_", " ").title(),
        )

    @classmethod
    def format_status(
        cls,
        value: str | Enum | None,
    ) -> str:
        """
        Traduce estados internos a etiquetas comerciales.
        """

        normalized_value = cls._normalize_enum_or_string(value)

        if not normalized_value:
            return "-"

        return cls.STATUS_LABELS.get(
            normalized_value,
            normalized_value.replace("_", " ").title(),
        )

    @staticmethod
    def format_boolean(value: bool | None) -> str:
        """
        Convierte booleanos en valores legibles.
        """

        if value is None:
            return "-"

        return "Sí" if value else "No"

    @staticmethod
    def format_nullable(
        value: Any,
        default: str = "-",
    ) -> str:
        """
        Normaliza textos opcionales.
        """

        if value is None:
            return default

        normalized_value = str(value).strip()

        return normalized_value or default

    @classmethod
    def _validate_report_schema(
        cls,
        *,
        report_type: ReportExportType,
        report: ReportSchema,
    ) -> None:
        expected_schema = cls.REPORT_SCHEMA_TYPES.get(
            report_type,
        )

        if expected_schema is None:
            raise ValueError(
                f"Tipo de reporte no soportado: {report_type.value}"
            )

        if not isinstance(report, expected_schema):
            raise TypeError(
                "El schema recibido no corresponde al reporte "
                f"{report_type.value}. Se esperaba "
                f"{expected_schema.__name__} y se recibió "
                f"{type(report).__name__}."
            )

    @staticmethod
    def _validate_period(
        *,
        start_date: date | None,
        end_date: date | None,
    ) -> None:
        if (
            start_date is not None
            and end_date is not None
            and start_date > end_date
        ):
            raise ValueError(
                "La fecha inicial no puede ser mayor que la fecha final."
            )

    @staticmethod
    def _validate_store(
        store: Mapping[str, Any],
    ) -> None:
        if not isinstance(store, Mapping):
            raise TypeError(
                "La información de tienda debe ser un mapping."
            )

        store_name = str(
            store.get("store_name", "")
        ).strip()

        if not store_name:
            raise ValueError(
                "El nombre de la tienda es obligatorio."
            )

    @staticmethod
    def _validate_dataset(
        dataset: ReportExportDataset,
    ) -> None:
        if not isinstance(dataset, dict):
            raise TypeError(
                "El dataset exportable debe ser un diccionario."
            )

        required_keys = {
            "summary",
            "columns",
            "rows",
        }

        missing_keys = required_keys.difference(
            dataset.keys()
        )

        if missing_keys:
            raise ValueError(
                "El dataset no contiene los campos obligatorios: "
                + ", ".join(sorted(missing_keys))
            )

        if not isinstance(dataset["summary"], list):
            raise TypeError(
                "El resumen debe ser una lista."
            )

        if not isinstance(dataset["columns"], list):
            raise TypeError(
                "Las columnas deben ser una lista."
            )

        if not isinstance(dataset["rows"], list):
            raise TypeError(
                "Las filas deben ser una lista."
            )

        if not dataset["columns"]:
            raise ValueError(
                "El dataset debe contener al menos una columna."
            )

        column_keys: set[str] = set()

        for index, column in enumerate(
            dataset["columns"],
            start=1,
        ):
            key = str(column.get("key", "")).strip()
            label = str(column.get("label", "")).strip()

            if not key:
                raise ValueError(
                    f"La columna {index} no tiene clave."
                )

            if not label:
                raise ValueError(
                    f"La columna {index} no tiene etiqueta."
                )

            if key in column_keys:
                raise ValueError(
                    f"La columna está duplicada: {key}"
                )

            column_keys.add(key)

    @staticmethod
    def _to_decimal(
        value: Decimal | int | float | str | None,
        default: str = "0.00",
    ) -> Decimal:
        if value is None:
            return Decimal(default)

        if isinstance(value, Decimal):
            return value

        return Decimal(str(value))

    @staticmethod
    def _normalize_enum_or_string(
        value: str | Enum | None,
    ) -> str:
        if value is None:
            return ""

        if isinstance(value, Enum):
            value = value.value

        return str(value).strip().upper()

    @staticmethod
    def _not_implemented(
        report_name: str,
    ) -> ReportExportDataset:
        """
        Mensaje temporal mientras se completan los adaptadores específicos.
        """

        raise NotImplementedError(
            f"El adaptador de {report_name} todavía no está implementado."
        )

    @classmethod
    def _adapt_sales(
        cls,
        report: SalesReportSchema,
    ) -> ReportExportDataset:
        columns: list[ReportExportColumn] = [
            {
                "key": "sale_id",
                "label": "Venta",
                "format": "integer",
                "alignment": "text-center",
                "width": 5,
            },
            {
                "key": "created_at",
                "label": "Fecha",
                "format": "datetime",
                "alignment": "text-center",
                "width": 10,
            },
            {
                "key": "customer_name",
                "label": "Cliente",
                "alignment": "text-left",
                "width": 14,
            },
            {
                "key": "document_type",
                "label": "Comprobante",
                "alignment": "text-center",
                "width": 9,
            },
            {
                "key": "payment_method",
                "label": "Pago",
                "alignment": "text-center",
                "width": 7,
            },
            {
                "key": "items_quantity",
                "label": "Cantidad",
                "format": "quantity",
                "alignment": "text-right",
                "width": 7,
            },
            {
                "key": "subtotal",
                "label": "Subtotal",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "discount_amount",
                "label": "Descuento",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "total_amount",
                "label": "Total",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "total_cost",
                "label": "Costo",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "profit_amount",
                "label": "Ganancia",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "status",
                "label": "Estado",
                "alignment": "text-center",
                "width": 8,
            },
        ]

        rows = [
            {
                "sale_id": item.sale_id,
                "created_at": item.created_at,
                "customer_name": cls.format_nullable(
                    item.customer_name,
                    default="Público general",
                ),
                "document_type": cls.format_document_type(
                    item.document_type,
                ),
                "payment_method": cls.format_payment_method(
                    item.payment_method,
                ),
                "items_quantity": item.items_quantity,
                "subtotal": item.subtotal,
                "discount_amount": item.discount_amount,
                "total_amount": item.total_amount,
                "total_cost": item.total_cost,
                "profit_amount": item.profit_amount,
                "status": (
                    "Confirmada"
                    if item.is_confirmed
                    else "Pendiente"
                ),
            }
            for item in report.items
        ]

        summary: list[ReportExportSummaryItem] = [
            {
                "label": "Ventas",
                "value": str(report.total_sales_count),
            },
            {
                "label": "Total vendido",
                "value": cls.format_currency(
                    report.total_sales_amount,
                ),
            },
            {
                "label": "Ganancia",
                "value": cls.format_currency(
                    report.total_profit_amount,
                ),
            },
            {
                "label": "Descuentos",
                "value": cls.format_currency(
                    report.total_discounts,
                ),
            },
            {
                "label": "Efectivo",
                "value": cls.format_currency(
                    report.cash_sales_amount,
                ),
            },
            {
                "label": "Yape",
                "value": cls.format_currency(
                    report.yape_sales_amount,
                ),
            },
            {
                "label": "Fiado",
                "value": cls.format_currency(
                    report.credit_sales_amount,
                ),
            },
            {
                "label": "Costo total",
                "value": cls.format_currency(
                    report.total_cost_amount,
                ),
            },
        ]

        return {
            "summary": summary,
            "columns": columns,
            "rows": rows,
        }

    @classmethod
    def _adapt_purchases(
        cls,
        report: PurchasesReportSchema,
    ) -> ReportExportDataset:
        columns: list[ReportExportColumn] = [
            {
                "key": "purchase_id",
                "label": "Compra",
                "format": "integer",
                "alignment": "text-center",
                "width": 6,
            },
            {
                "key": "purchase_date",
                "label": "Fecha",
                "format": "date",
                "alignment": "text-center",
                "width": 9,
            },
            {
                "key": "supplier_name",
                "label": "Proveedor",
                "alignment": "text-left",
                "width": 17,
            },
            {
                "key": "document_type",
                "label": "Documento",
                "alignment": "text-center",
                "width": 10,
            },
            {
                "key": "document_number",
                "label": "Número",
                "alignment": "text-center",
                "width": 11,
            },
            {
                "key": "items_count",
                "label": "Productos",
                "format": "integer",
                "alignment": "text-right",
                "width": 7,
            },
            {
                "key": "total_units",
                "label": "Unidades",
                "format": "quantity",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "subtotal",
                "label": "Subtotal",
                "format": "currency",
                "alignment": "text-right",
                "width": 9,
            },
            {
                "key": "tax_amount",
                "label": "Impuesto",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "total_amount",
                "label": "Total",
                "format": "currency",
                "alignment": "text-right",
                "width": 9,
            },
            {
                "key": "status",
                "label": "Estado",
                "alignment": "text-center",
                "width": 8,
            },
        ]

        rows = [
            {
                "purchase_id": item.purchase_id,
                "purchase_date": item.purchase_date,
                "supplier_name": cls.format_nullable(
                    item.supplier_name,
                ),
                "document_type": cls.format_document_type(
                    item.document_type,
                ),
                "document_number": cls.format_nullable(
                    item.document_number,
                ),
                "items_count": item.items_count,
                "total_units": item.total_units,
                "subtotal": item.subtotal,
                "tax_amount": item.tax_amount,
                "total_amount": item.total_amount,
                "status": (
                    "Confirmada"
                    if item.is_confirmed
                    else "Pendiente"
                ),
            }
            for item in report.items
        ]

        summary: list[ReportExportSummaryItem] = [
            {
                "label": "Compras",
                "value": str(report.total_purchases_count),
            },
            {
                "label": "Total comprado",
                "value": cls.format_currency(
                    report.total_purchases_amount,
                ),
            },
            {
                "label": "Subtotal",
                "value": cls.format_currency(
                    report.total_subtotal,
                ),
            },
            {
                "label": "Impuestos",
                "value": cls.format_currency(
                    report.total_tax_amount,
                ),
            },
            {
                "label": "Unidades",
                "value": cls.format_quantity(
                    report.total_units,
                ),
            },
        ]

        return {
            "summary": summary,
            "columns": columns,
            "rows": rows,
        }

    @classmethod
    def _adapt_inventory(
        cls,
        report: InventoryReportSchema,
    ) -> ReportExportDataset:
        columns: list[ReportExportColumn] = [
            {
                "key": "internal_code",
                "label": "Código",
                "alignment": "text-center",
                "width": 7,
            },
            {
                "key": "name",
                "label": "Producto",
                "alignment": "text-left",
                "width": 15,
            },
            {
                "key": "brand",
                "label": "Marca",
                "alignment": "text-left",
                "width": 9,
            },
            {
                "key": "category_name",
                "label": "Categoría",
                "alignment": "text-left",
                "width": 9,
            },
            {
                "key": "supplier_name",
                "label": "Proveedor",
                "alignment": "text-left",
                "width": 11,
            },
            {
                "key": "cost_price",
                "label": "Costo",
                "format": "currency",
                "alignment": "text-right",
                "width": 7,
            },
            {
                "key": "sale_price",
                "label": "Precio",
                "format": "currency",
                "alignment": "text-right",
                "width": 7,
            },
            {
                "key": "stock",
                "label": "Stock",
                "format": "quantity",
                "alignment": "text-right",
                "width": 7,
            },
            {
                "key": "minimum_stock",
                "label": "Mínimo",
                "format": "quantity",
                "alignment": "text-right",
                "width": 7,
            },
            {
                "key": "stock_cost_value",
                "label": "Valor costo",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "stock_sale_value",
                "label": "Valor venta",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "projected_profit",
                "label": "Utilidad",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "expiration_date",
                "label": "Vencimiento",
                "format": "date",
                "alignment": "text-center",
                "width": 8,
            },
            {
                "key": "status",
                "label": "Estado",
                "alignment": "text-center",
                "width": 8,
            },
        ]

        rows = [
            {
                "internal_code": cls.format_nullable(
                    item.internal_code,
                ),
                "name": item.name,
                "brand": cls.format_nullable(item.brand),
                "category_name": cls.format_nullable(
                    item.category_name,
                ),
                "supplier_name": cls.format_nullable(
                    item.supplier_name,
                ),
                "cost_price": item.cost_price,
                "sale_price": item.sale_price,
                "stock": item.stock,
                "minimum_stock": item.minimum_stock,
                "stock_cost_value": item.stock_cost_value,
                "stock_sale_value": item.stock_sale_value,
                "projected_profit": item.projected_profit,
                "expiration_date": item.expiration_date,
                "status": cls.format_status(item.status),
            }
            for item in report.items
        ]

        summary: list[ReportExportSummaryItem] = [
            {
                "label": "Productos",
                "value": str(report.total_products),
            },
            {
                "label": "Stock total",
                "value": cls.format_quantity(
                    report.total_stock_quantity,
                ),
            },
            {
                "label": "Valor de costo",
                "value": cls.format_currency(
                    report.total_stock_cost_value,
                ),
            },
            {
                "label": "Valor de venta",
                "value": cls.format_currency(
                    report.total_stock_sale_value,
                ),
            },
            {
                "label": "Utilidad proyectada",
                "value": cls.format_currency(
                    report.total_projected_profit,
                ),
            },
            {
                "label": "Stock bajo",
                "value": str(
                    report.low_stock_products_count
                ),
            },
            {
                "label": "Sin stock",
                "value": str(
                    report.out_of_stock_products_count
                ),
            },
            {
                "label": "Próximos a vencer",
                "value": str(
                    report.expiring_products_count
                ),
            },
        ]

        return {
            "summary": summary,
            "columns": columns,
            "rows": rows,
        }

    @classmethod
    def _adapt_cash(
        cls,
        report: CashReportSchema,
    ) -> ReportExportDataset:
        columns: list[ReportExportColumn] = [
            {
                "key": "cash_register_id",
                "label": "Caja",
                "format": "integer",
                "alignment": "text-center",
                "width": 5,
            },
            {
                "key": "opened_at",
                "label": "Apertura",
                "format": "datetime",
                "alignment": "text-center",
                "width": 10,
            },
            {
                "key": "closed_at",
                "label": "Cierre",
                "format": "datetime",
                "alignment": "text-center",
                "width": 10,
            },
            {
                "key": "opening_amount",
                "label": "Monto inicial",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "cash_sales_amount",
                "label": "Efectivo",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "yape_sales_amount",
                "label": "Yape",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "credit_sales_amount",
                "label": "Fiado",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "manual_income_amount",
                "label": "Ingresos",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "manual_expense_amount",
                "label": "Egresos",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "total_sales_amount",
                "label": "Ventas",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "total_profit_amount",
                "label": "Ganancia",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "cash_difference_amount",
                "label": "Dif. efectivo",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "yape_difference_amount",
                "label": "Dif. Yape",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "status",
                "label": "Estado",
                "alignment": "text-center",
                "width": 7,
            },
        ]

        rows = [
            {
                "cash_register_id": item.cash_register_id,
                "opened_at": item.opened_at,
                "closed_at": item.closed_at,
                "opening_amount": item.opening_amount,
                "cash_sales_amount": item.cash_sales_amount,
                "yape_sales_amount": item.yape_sales_amount,
                "credit_sales_amount": item.credit_sales_amount,
                "manual_income_amount": item.manual_income_amount,
                "manual_expense_amount": item.manual_expense_amount,
                "total_sales_amount": item.total_sales_amount,
                "total_profit_amount": item.total_profit_amount,
                "cash_difference_amount": (
                    item.cash_difference_amount
                    if item.cash_difference_amount is not None
                    else Decimal("0.00")
                ),
                "yape_difference_amount": (
                    item.yape_difference_amount
                    if item.yape_difference_amount is not None
                    else Decimal("0.00")
                ),
                "status": cls.format_status(item.status),
            }
            for item in report.items
        ]

        summary: list[ReportExportSummaryItem] = [
            {
                "label": "Cajas",
                "value": str(report.total_registers),
            },
            {
                "label": "Ventas",
                "value": cls.format_currency(
                    report.total_sales_amount,
                ),
            },
            {
                "label": "Ganancia",
                "value": cls.format_currency(
                    report.total_profit_amount,
                ),
            },
            {
                "label": "Efectivo",
                "value": cls.format_currency(
                    report.total_cash_sales_amount,
                ),
            },
            {
                "label": "Yape",
                "value": cls.format_currency(
                    report.total_yape_sales_amount,
                ),
            },
            {
                "label": "Fiado",
                "value": cls.format_currency(
                    report.total_credit_sales_amount,
                ),
            },
            {
                "label": "Ingresos manuales",
                "value": cls.format_currency(
                    report.total_manual_income_amount,
                ),
            },
            {
                "label": "Egresos manuales",
                "value": cls.format_currency(
                    report.total_manual_expense_amount,
                ),
            },
        ]

        return {
            "summary": summary,
            "columns": columns,
            "rows": rows,
        }

    @classmethod
    def _adapt_customers(
        cls,
        report: CustomersReportSchema,
    ) -> ReportExportDataset:
        columns: list[ReportExportColumn] = [
            {
                "key": "full_name",
                "label": "Cliente",
                "alignment": "text-left",
                "width": 15,
            },
            {
                "key": "document_number",
                "label": "Documento",
                "alignment": "text-center",
                "width": 9,
            },
            {
                "key": "phone",
                "label": "Teléfono",
                "alignment": "text-center",
                "width": 9,
            },
            {
                "key": "whatsapp",
                "label": "WhatsApp",
                "alignment": "text-center",
                "width": 9,
            },
            {
                "key": "purchases_count",
                "label": "Compras",
                "format": "integer",
                "alignment": "text-right",
                "width": 6,
            },
            {
                "key": "total_purchased_amount",
                "label": "Total comprado",
                "format": "currency",
                "alignment": "text-right",
                "width": 9,
            },
            {
                "key": "total_profit_generated",
                "label": "Ganancia",
                "format": "currency",
                "alignment": "text-right",
                "width": 9,
            },
            {
                "key": "total_credit_amount",
                "label": "Total fiado",
                "format": "currency",
                "alignment": "text-right",
                "width": 9,
            },
            {
                "key": "total_debt_paid_amount",
                "label": "Pagado",
                "format": "currency",
                "alignment": "text-right",
                "width": 9,
            },
            {
                "key": "pending_debt_amount",
                "label": "Deuda",
                "format": "currency",
                "alignment": "text-right",
                "width": 9,
            },
            {
                "key": "last_purchase_date",
                "label": "Última compra",
                "format": "datetime",
                "alignment": "text-center",
                "width": 10,
            },
            {
                "key": "status",
                "label": "Estado",
                "alignment": "text-center",
                "width": 7,
            },
        ]

        rows = [
            {
                "full_name": item.full_name,
                "document_number": cls.format_nullable(
                    item.document_number,
                ),
                "phone": cls.format_nullable(item.phone),
                "whatsapp": cls.format_nullable(item.whatsapp),
                "purchases_count": item.purchases_count,
                "total_purchased_amount": (
                    item.total_purchased_amount
                ),
                "total_profit_generated": (
                    item.total_profit_generated
                ),
                "total_credit_amount": (
                    item.total_credit_amount
                ),
                "total_debt_paid_amount": (
                    item.total_debt_paid_amount
                ),
                "pending_debt_amount": (
                    item.pending_debt_amount
                ),
                "last_purchase_date": item.last_purchase_date,
                "status": (
                    "Activo"
                    if item.is_active
                    else "Inactivo"
                ),
            }
            for item in report.items
        ]

        summary: list[ReportExportSummaryItem] = [
            {
                "label": "Clientes",
                "value": str(report.total_customers),
            },
            {
                "label": "Clientes activos",
                "value": str(report.active_customers),
            },
            {
                "label": "Con compras",
                "value": str(
                    report.customers_with_purchases
                ),
            },
            {
                "label": "Con deuda",
                "value": str(report.customers_with_debt),
            },
            {
                "label": "Total comprado",
                "value": cls.format_currency(
                    report.total_purchased_amount,
                ),
            },
            {
                "label": "Deuda pendiente",
                "value": cls.format_currency(
                    report.total_pending_debt_amount,
                ),
            },
        ]

        return {
            "summary": summary,
            "columns": columns,
            "rows": rows,
        }

    @classmethod
    def _adapt_debts(
        cls,
        report: DebtsReportSchema,
    ) -> ReportExportDataset:
        columns: list[ReportExportColumn] = [
            {
                "key": "debt_id",
                "label": "Fiado",
                "format": "integer",
                "alignment": "text-center",
                "width": 6,
            },
            {
                "key": "sale_id",
                "label": "Venta",
                "format": "integer",
                "alignment": "text-center",
                "width": 6,
            },
            {
                "key": "customer_name",
                "label": "Cliente",
                "alignment": "text-left",
                "width": 18,
            },
            {
                "key": "created_at",
                "label": "Fecha",
                "format": "datetime",
                "alignment": "text-center",
                "width": 11,
            },
            {
                "key": "original_amount",
                "label": "Monto original",
                "format": "currency",
                "alignment": "text-right",
                "width": 10,
            },
            {
                "key": "paid_amount",
                "label": "Pagado",
                "format": "currency",
                "alignment": "text-right",
                "width": 9,
            },
            {
                "key": "pending_amount",
                "label": "Pendiente",
                "format": "currency",
                "alignment": "text-right",
                "width": 9,
            },
            {
                "key": "payments_count",
                "label": "Pagos",
                "format": "integer",
                "alignment": "text-right",
                "width": 7,
            },
            {
                "key": "last_payment_date",
                "label": "Último pago",
                "format": "datetime",
                "alignment": "text-center",
                "width": 11,
            },
            {
                "key": "status",
                "label": "Estado",
                "alignment": "text-center",
                "width": 8,
            },
        ]

        rows = [
            {
                "debt_id": item.debt_id,
                "sale_id": item.sale_id,
                "customer_name": item.customer_name,
                "created_at": item.created_at,
                "original_amount": item.original_amount,
                "paid_amount": item.paid_amount,
                "pending_amount": item.pending_amount,
                "payments_count": item.payments_count,
                "last_payment_date": item.last_payment_date,
                "status": cls.format_status(item.status),
            }
            for item in report.items
        ]

        summary: list[ReportExportSummaryItem] = [
            {
                "label": "Fiados",
                "value": str(report.total_debts),
            },
            {
                "label": "Pendientes",
                "value": str(report.pending_debts),
            },
            {
                "label": "Parciales",
                "value": str(report.partial_debts),
            },
            {
                "label": "Pagados",
                "value": str(report.paid_debts),
            },
            {
                "label": "Monto original",
                "value": cls.format_currency(
                    report.total_original_amount,
                ),
            },
            {
                "label": "Total pagado",
                "value": cls.format_currency(
                    report.total_paid_amount,
                ),
            },
            {
                "label": "Saldo pendiente",
                "value": cls.format_currency(
                    report.total_pending_amount,
                ),
            },
        ]

        return {
            "summary": summary,
            "columns": columns,
            "rows": rows,
        }

    @classmethod
    def _adapt_products(
        cls,
        report: ProductsReportSchema,
    ) -> ReportExportDataset:
        columns: list[ReportExportColumn] = [
            {
                "key": "internal_code",
                "label": "Código",
                "alignment": "text-center",
                "width": 7,
            },
            {
                "key": "name",
                "label": "Producto",
                "alignment": "text-left",
                "width": 14,
            },
            {
                "key": "brand",
                "label": "Marca",
                "alignment": "text-left",
                "width": 8,
            },
            {
                "key": "category_name",
                "label": "Categoría",
                "alignment": "text-left",
                "width": 9,
            },
            {
                "key": "supplier_name",
                "label": "Proveedor",
                "alignment": "text-left",
                "width": 10,
            },
            {
                "key": "cost_price",
                "label": "Costo",
                "format": "currency",
                "alignment": "text-right",
                "width": 7,
            },
            {
                "key": "sale_price",
                "label": "Precio",
                "format": "currency",
                "alignment": "text-right",
                "width": 7,
            },
            {
                "key": "profit_margin",
                "label": "Margen",
                "format": "percentage",
                "alignment": "text-right",
                "width": 7,
            },
            {
                "key": "stock",
                "label": "Stock",
                "format": "quantity",
                "alignment": "text-right",
                "width": 7,
            },
            {
                "key": "sold_quantity",
                "label": "Vendido",
                "format": "quantity",
                "alignment": "text-right",
                "width": 7,
            },
            {
                "key": "sales_amount",
                "label": "Ventas",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "generated_profit",
                "label": "Ganancia",
                "format": "currency",
                "alignment": "text-right",
                "width": 8,
            },
            {
                "key": "expiration_date",
                "label": "Vencimiento",
                "format": "date",
                "alignment": "text-center",
                "width": 8,
            },
            {
                "key": "status",
                "label": "Estado",
                "alignment": "text-center",
                "width": 7,
            },
        ]

        rows = [
            {
                "internal_code": cls.format_nullable(
                    item.internal_code,
                ),
                "name": item.name,
                "brand": cls.format_nullable(item.brand),
                "category_name": cls.format_nullable(
                    item.category_name,
                ),
                "supplier_name": cls.format_nullable(
                    item.supplier_name,
                ),
                "cost_price": item.cost_price,
                "sale_price": item.sale_price,
                "profit_margin": item.profit_margin,
                "stock": item.stock,
                "sold_quantity": item.sold_quantity,
                "sales_amount": item.sales_amount,
                "generated_profit": item.generated_profit,
                "expiration_date": item.expiration_date,
                "status": cls.format_status(item.status),
            }
            for item in report.items
        ]

        summary: list[ReportExportSummaryItem] = [
            {
                "label": "Productos",
                "value": str(report.total_products),
            },
            {
                "label": "Activos",
                "value": str(report.active_products),
            },
            {
                "label": "Inactivos",
                "value": str(report.inactive_products),
            },
            {
                "label": "Stock bajo",
                "value": str(report.low_stock_products),
            },
            {
                "label": "Con ventas",
                "value": str(report.products_with_sales),
            },
            {
                "label": "Cantidad vendida",
                "value": cls.format_quantity(
                    report.total_sold_quantity,
                ),
            },
            {
                "label": "Total vendido",
                "value": cls.format_currency(
                    report.total_sales_amount,
                ),
            },
            {
                "label": "Ganancia generada",
                "value": cls.format_currency(
                    report.total_generated_profit,
                ),
            },
        ]

        return {
            "summary": summary,
            "columns": columns,
            "rows": rows,
        }

    @classmethod
    def _adapt_suppliers(
        cls,
        report: SuppliersReportSchema,
    ) -> ReportExportDataset:
        columns: list[ReportExportColumn] = [
            {
                "key": "name",
                "label": "Proveedor",
                "alignment": "text-left",
                "width": 18,
            },
            {
                "key": "ruc",
                "label": "RUC",
                "alignment": "text-center",
                "width": 10,
            },
            {
                "key": "phone",
                "label": "Teléfono",
                "alignment": "text-center",
                "width": 9,
            },
            {
                "key": "whatsapp",
                "label": "WhatsApp",
                "alignment": "text-center",
                "width": 9,
            },
            {
                "key": "email",
                "label": "Correo",
                "alignment": "text-left",
                "width": 14,
            },
            {
                "key": "contact_name",
                "label": "Contacto",
                "alignment": "text-left",
                "width": 11,
            },
            {
                "key": "products_count",
                "label": "Productos",
                "format": "integer",
                "alignment": "text-right",
                "width": 7,
            },
            {
                "key": "purchases_count",
                "label": "Compras",
                "format": "integer",
                "alignment": "text-right",
                "width": 7,
            },
            {
                "key": "total_purchased_amount",
                "label": "Total comprado",
                "format": "currency",
                "alignment": "text-right",
                "width": 10,
            },
            {
                "key": "last_purchase_date",
                "label": "Última compra",
                "format": "datetime",
                "alignment": "text-center",
                "width": 10,
            },
            {
                "key": "status",
                "label": "Estado",
                "alignment": "text-center",
                "width": 7,
            },
        ]

        rows = [
            {
                "name": item.name,
                "ruc": cls.format_nullable(item.ruc),
                "phone": cls.format_nullable(item.phone),
                "whatsapp": cls.format_nullable(item.whatsapp),
                "email": cls.format_nullable(item.email),
                "contact_name": cls.format_nullable(
                    item.contact_name,
                ),
                "products_count": item.products_count,
                "purchases_count": item.purchases_count,
                "total_purchased_amount": (
                    item.total_purchased_amount
                ),
                "last_purchase_date": item.last_purchase_date,
                "status": (
                    "Activo"
                    if item.is_active
                    else "Inactivo"
                ),
            }
            for item in report.items
        ]

        summary: list[ReportExportSummaryItem] = [
            {
                "label": "Proveedores",
                "value": str(report.total_suppliers),
            },
            {
                "label": "Activos",
                "value": str(report.active_suppliers),
            },
            {
                "label": "Con productos",
                "value": str(
                    report.suppliers_with_products
                ),
            },
            {
                "label": "Con compras",
                "value": str(
                    report.suppliers_with_purchases
                ),
            },
            {
                "label": "Total comprado",
                "value": cls.format_currency(
                    report.total_purchased_amount,
                ),
            },
        ]

        return {
            "summary": summary,
            "columns": columns,
            "rows": rows,
        }