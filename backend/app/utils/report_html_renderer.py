from collections.abc import Mapping
from pathlib import Path
from typing import Any

from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
    TemplateError,
    select_autoescape,
)


class ReportHtmlRenderer:
    """
    Renderizador HTML reutilizable para reportes PDF.

    Recibe un contexto previamente preparado y lo transforma en HTML
    mediante la plantilla oficial de reportes de NovaPOS.
    """

    TEMPLATE_NAME = "reports/report_export.html"

    REQUIRED_CONTEXT_KEYS = {
        "report_title",
        "report_type",
        "generated_at",
        "start_date",
        "end_date",
        "store",
        "summary",
        "columns",
        "rows",
    }

    @classmethod
    def render(
        cls,
        context: Mapping[str, Any],
    ) -> str:
        """
        Renderiza la plantilla oficial de reportes.

        Args:
            context:
                Diccionario con toda la información preparada para
                presentación.

        Returns:
            Documento HTML completo.
        """

        cls._validate_context(context)

        environment = cls._build_environment()

        try:
            template = environment.get_template(
                cls.TEMPLATE_NAME,
            )

            html_content = template.render(
                **dict(context),
            )

        except TemplateError as exc:
            raise RuntimeError(
                "No fue posible renderizar la plantilla HTML del reporte."
            ) from exc

        cls._validate_rendered_html(html_content)

        return html_content

    @classmethod
    def validate_template(cls) -> bool:
        """
        Verifica que la plantilla oficial exista y pueda cargarse.
        """

        environment = cls._build_environment()

        try:
            environment.get_template(
                cls.TEMPLATE_NAME,
            )
        except TemplateError as exc:
            raise RuntimeError(
                "La plantilla oficial de reportes no pudo ser cargada."
            ) from exc

        return True

    @classmethod
    def _build_environment(cls) -> Environment:
        """
        Construye el entorno Jinja2 utilizado por el renderizador.
        """

        templates_directory = cls._get_templates_directory()

        return Environment(
            loader=FileSystemLoader(
                str(templates_directory),
            ),
            autoescape=select_autoescape(
                enabled_extensions=("html", "xml"),
                default_for_string=True,
                default=True,
            ),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    @classmethod
    def _get_templates_directory(cls) -> Path:
        """
        Obtiene la carpeta oficial backend/app/templates.
        """

        app_directory = Path(__file__).resolve().parent.parent
        templates_directory = app_directory / "templates"

        if not templates_directory.exists():
            raise RuntimeError(
                "No existe la carpeta oficial app/templates."
            )

        if not templates_directory.is_dir():
            raise RuntimeError(
                "La ruta app/templates no corresponde a una carpeta."
            )

        return templates_directory

    @classmethod
    def _validate_context(
        cls,
        context: Mapping[str, Any],
    ) -> None:
        """
        Valida la estructura mínima requerida por la plantilla.
        """

        if not isinstance(context, Mapping):
            raise TypeError(
                "El contexto del reporte debe ser un mapping."
            )

        missing_keys = sorted(
            cls.REQUIRED_CONTEXT_KEYS.difference(
                context.keys(),
            )
        )

        if missing_keys:
            raise ValueError(
                "Faltan campos obligatorios en el contexto del reporte: "
                + ", ".join(missing_keys)
            )

        report_title = str(
            context.get("report_title", "")
        ).strip()

        report_type = str(
            context.get("report_type", "")
        ).strip()

        if not report_title:
            raise ValueError(
                "El título del reporte es obligatorio."
            )

        if not report_type:
            raise ValueError(
                "El tipo de reporte es obligatorio."
            )

        store = context.get("store")

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

        summary = context.get("summary")
        columns = context.get("columns")
        rows = context.get("rows")

        if not isinstance(summary, list):
            raise TypeError(
                "El resumen del reporte debe ser una lista."
            )

        if not isinstance(columns, list):
            raise TypeError(
                "Las columnas del reporte deben ser una lista."
            )

        if not isinstance(rows, list):
            raise TypeError(
                "Las filas del reporte deben ser una lista."
            )

        if not columns:
            raise ValueError(
                "El reporte debe contener al menos una columna."
            )

        cls._validate_columns(columns)

    @staticmethod
    def _validate_columns(
        columns: list[Any],
    ) -> None:
        """
        Valida las definiciones visuales de las columnas.
        """

        allowed_alignments = {
            "text-left",
            "text-center",
            "text-right",
        }

        column_keys: set[str] = set()

        for index, column in enumerate(
            columns,
            start=1,
        ):
            if not isinstance(column, Mapping):
                raise TypeError(
                    f"La columna {index} debe ser un mapping."
                )

            key = str(
                column.get("key", "")
            ).strip()

            label = str(
                column.get("label", "")
            ).strip()

            alignment = str(
                column.get(
                    "alignment",
                    "text-left",
                )
            ).strip()

            if not key:
                raise ValueError(
                    f"La columna {index} no tiene una clave válida."
                )

            if not label:
                raise ValueError(
                    f"La columna {index} no tiene una etiqueta válida."
                )

            if key in column_keys:
                raise ValueError(
                    f"La clave de columna está duplicada: {key}"
                )

            if alignment not in allowed_alignments:
                raise ValueError(
                    "La alineación de columna no es válida: "
                    f"{alignment}"
                )

            width = column.get("width")

            if width is not None:
                try:
                    numeric_width = float(width)
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"El ancho de la columna {key} no es válido."
                    ) from exc

                if numeric_width <= 0 or numeric_width > 100:
                    raise ValueError(
                        f"El ancho de la columna {key} debe estar "
                        "entre 0 y 100."
                    )

            column_keys.add(key)

    @staticmethod
    def _validate_rendered_html(
        html_content: str,
    ) -> None:
        """
        Verifica que Jinja2 haya producido un documento HTML utilizable.
        """

        if not html_content or not html_content.strip():
            raise RuntimeError(
                "La plantilla generó contenido HTML vacío."
            )

        normalized_html = html_content.lower()

        if "<html" not in normalized_html:
            raise RuntimeError(
                "El contenido generado no contiene la etiqueta HTML."
            )

        if "</html>" not in normalized_html:
            raise RuntimeError(
                "El contenido generado no cierra la etiqueta HTML."
            )

        if "<table" not in normalized_html:
            raise RuntimeError(
                "El contenido generado no contiene la tabla del reporte."
            )