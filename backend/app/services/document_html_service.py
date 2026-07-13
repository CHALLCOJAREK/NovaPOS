from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape


class DocumentHtmlService:
    TEMPLATE_DIRECTORY = Path(
        "app/templates/receipts"
    )

    TEMPLATE_NAME = "sale_receipt.html"

    _environment = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIRECTORY)),
        autoescape=select_autoescape(
            enabled_extensions=("html", "xml"),
        ),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    @classmethod
    def render_sale_receipt(
        cls,
        context: dict[str, Any],
    ) -> str:
        if not context:
            raise ValueError(
                "El contexto del comprobante es obligatorio"
            )

        try:
            template = cls._environment.get_template(
                cls.TEMPLATE_NAME
            )
        except TemplateNotFound as exc:
            raise RuntimeError(
                "No se encontró la plantilla HTML del comprobante"
            ) from exc

        html_content = template.render(**context)

        if not html_content.strip():
            raise RuntimeError(
                "La plantilla del comprobante generó contenido vacío"
            )

        return html_content