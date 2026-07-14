from pathlib import Path
from typing import Literal

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


class ReportPdfGenerator:
    """
    Generador reutilizable de reportes profesionales en formato PDF.

    Este componente no consulta la base de datos ni contiene lógica de
    negocio. Su única responsabilidad es convertir HTML previamente
    renderizado en un archivo PDF.
    """

    PAGE_FORMAT = "A4"

    DEFAULT_MARGIN_TOP = "14mm"
    DEFAULT_MARGIN_RIGHT = "12mm"
    DEFAULT_MARGIN_BOTTOM = "14mm"
    DEFAULT_MARGIN_LEFT = "12mm"

    DEFAULT_TIMEOUT_MS = 60_000

    @classmethod
    def generate(
        cls,
        *,
        html_content: str,
        file_path: Path | str,
        orientation: Literal["portrait", "landscape"] = "landscape",
        margin_top: str = DEFAULT_MARGIN_TOP,
        margin_right: str = DEFAULT_MARGIN_RIGHT,
        margin_bottom: str = DEFAULT_MARGIN_BOTTOM,
        margin_left: str = DEFAULT_MARGIN_LEFT,
    ) -> Path:
        """
        Genera un archivo PDF a partir de contenido HTML.

        Args:
            html_content:
                Documento HTML completo que será convertido a PDF.

            file_path:
                Ruta física donde se guardará el archivo generado.

            orientation:
                Orientación del documento: portrait o landscape.

            margin_top:
                Margen superior CSS aceptado por Playwright.

            margin_right:
                Margen derecho CSS aceptado por Playwright.

            margin_bottom:
                Margen inferior CSS aceptado por Playwright.

            margin_left:
                Margen izquierdo CSS aceptado por Playwright.

        Returns:
            Ruta absoluta del PDF generado.
        """

        destination = Path(file_path).expanduser().resolve()

        cls._validate_input(
            html_content=html_content,
            destination=destination,
            orientation=orientation,
            margins={
                "margin_top": margin_top,
                "margin_right": margin_right,
                "margin_bottom": margin_bottom,
                "margin_left": margin_left,
            },
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    headless=True,
                )

                try:
                    page = browser.new_page()

                    page.set_default_timeout(
                        cls.DEFAULT_TIMEOUT_MS,
                    )

                    page.set_content(
                        html_content,
                        wait_until="networkidle",
                    )

                    page.emulate_media(
                        media="print",
                    )

                    page.pdf(
                        path=str(destination),
                        format=cls.PAGE_FORMAT,
                        landscape=orientation == "landscape",
                        print_background=True,
                        prefer_css_page_size=False,
                        margin={
                            "top": margin_top,
                            "right": margin_right,
                            "bottom": margin_bottom,
                            "left": margin_left,
                        },
                    )
                finally:
                    browser.close()

        except PlaywrightError as exc:
            cls._remove_incomplete_file(destination)

            raise RuntimeError(
                "No fue posible generar el reporte PDF mediante Playwright."
            ) from exc

        except Exception:
            cls._remove_incomplete_file(destination)
            raise

        cls._validate_generated_file(destination)

        return destination

    @classmethod
    def _validate_input(
        cls,
        *,
        html_content: str,
        destination: Path,
        orientation: str,
        margins: dict[str, str],
    ) -> None:
        """
        Valida los argumentos requeridos antes de abrir Chromium.
        """

        if destination.suffix.lower() != ".pdf":
            raise ValueError(
                "La ruta del reporte PDF debe terminar en .pdf."
            )

        if not html_content or not html_content.strip():
            raise ValueError(
                "El contenido HTML del reporte es obligatorio."
            )

        if orientation not in {"portrait", "landscape"}:
            raise ValueError(
                "La orientación debe ser portrait o landscape."
            )

        for margin_name, margin_value in margins.items():
            if not margin_value or not margin_value.strip():
                raise ValueError(
                    f"El valor de {margin_name} es obligatorio."
                )

    @staticmethod
    def _validate_generated_file(destination: Path) -> None:
        """
        Confirma que Playwright haya generado un archivo PDF válido.
        """

        if not destination.exists():
            raise RuntimeError(
                "El archivo PDF no fue generado."
            )

        if not destination.is_file():
            raise RuntimeError(
                "La ruta generada no corresponde a un archivo."
            )

        if destination.stat().st_size <= 0:
            destination.unlink(missing_ok=True)

            raise RuntimeError(
                "El archivo PDF generado está vacío."
            )

        with destination.open("rb") as pdf_file:
            signature = pdf_file.read(5)

        if signature != b"%PDF-":
            destination.unlink(missing_ok=True)

            raise RuntimeError(
                "El archivo generado no contiene una firma PDF válida."
            )

    @staticmethod
    def _remove_incomplete_file(destination: Path) -> None:
        """
        Elimina archivos incompletos cuando ocurre un error.
        """

        if destination.exists() and destination.is_file():
            destination.unlink(missing_ok=True)