from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from app.core.config import settings


class DocumentPdfService:
    OUTPUT_DIRECTORY = (
        Path(settings.UPLOAD_PATH)
        / "comprobantes"
        / "pdf"
    )

    @classmethod
    def generate_from_html(
        cls,
        html_content: str,
        full_number: str,
    ) -> str:
        normalized_html = html_content.strip()

        if not normalized_html:
            raise ValueError(
                "El contenido HTML es obligatorio para generar el PDF"
            )

        safe_filename = cls._sanitize_filename(full_number)

        output_directory = cls.OUTPUT_DIRECTORY.resolve()

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = (
            output_directory / f"{safe_filename}.pdf"
        )

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    headless=True,
                )

                try:
                    page = browser.new_page(
                        viewport={
                            "width": 1240,
                            "height": 1754,
                        },
                    )

                    page.set_content(
                        normalized_html,
                        wait_until="networkidle",
                    )

                    page.emulate_media(
                        media="print",
                    )

                    page.pdf(
                        path=str(output_path),
                        format="A4",
                        print_background=True,
                        prefer_css_page_size=True,
                        margin={
                            "top": "0",
                            "right": "0",
                            "bottom": "0",
                            "left": "0",
                        },
                    )

                finally:
                    browser.close()

        except PlaywrightError as exc:
            cls._remove_incomplete_file(output_path)

            raise RuntimeError(
                "No se pudo generar el PDF del comprobante"
            ) from exc

        if not output_path.is_file():
            raise RuntimeError(
                "El archivo PDF del comprobante no fue creado"
            )

        if output_path.stat().st_size == 0:
            cls._remove_incomplete_file(output_path)

            raise RuntimeError(
                "El archivo PDF generado está vacío"
            )

        return str(output_path)

    @staticmethod
    def _sanitize_filename(
        full_number: str,
    ) -> str:
        normalized_number = full_number.strip()

        if not normalized_number:
            raise ValueError(
                "El número del comprobante es obligatorio"
            )

        invalid_characters = '<>:"/\\|?*'

        safe_filename = "".join(
            character
            if character not in invalid_characters
            else "_"
            for character in normalized_number
        )

        safe_filename = safe_filename.strip(" .")

        if not safe_filename:
            raise ValueError(
                "El número del comprobante no produce un nombre válido"
            )

        return safe_filename

    @staticmethod
    def _remove_incomplete_file(
        file_path: Path,
    ) -> None:
        if file_path.exists():
            file_path.unlink()