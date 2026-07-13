import base64
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from io import BytesIO

import qrcode
from qrcode.constants import ERROR_CORRECT_M


@dataclass(frozen=True)
class DocumentQrResult:
    content: str
    image_uri: str


class DocumentQrService:
    @classmethod
    def generate(
        cls,
        full_number: str,
        sale_id: int,
        issued_at: datetime,
        total_amount: Decimal,
    ) -> DocumentQrResult:
        content = cls.build_content(
            full_number=full_number,
            sale_id=sale_id,
            issued_at=issued_at,
            total_amount=total_amount,
        )

        image_uri = cls.generate_image_uri(content)

        return DocumentQrResult(
            content=content,
            image_uri=image_uri,
        )

    @staticmethod
    def build_content(
        full_number: str,
        sale_id: int,
        issued_at: datetime,
        total_amount: Decimal,
    ) -> str:
        normalized_number = full_number.strip()

        if not normalized_number:
            raise ValueError(
                "El número del comprobante es obligatorio para generar el QR"
            )

        if sale_id <= 0:
            raise ValueError(
                "El ID de la venta debe ser mayor que cero"
            )

        normalized_total = Decimal(str(total_amount)).quantize(
            Decimal("0.01")
        )

        return "\n".join(
            [
                "NovaPOS",
                f"Comprobante: {normalized_number}",
                f"Venta ID: {sale_id}",
                f"Fecha: {issued_at.strftime('%d/%m/%Y %H:%M:%S')}",
                f"Total: S/ {normalized_total:.2f}",
            ]
        )

    @staticmethod
    def generate_image_uri(
        content: str,
    ) -> str:
        if not content.strip():
            raise ValueError(
                "El contenido del QR no puede estar vacío"
            )

        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_M,
            box_size=8,
            border=2,
        )

        qr.add_data(content)
        qr.make(fit=True)

        image = qr.make_image(
            fill_color="black",
            back_color="white",
        )

        buffer = BytesIO()
        image.save(buffer, format="PNG")

        encoded_image = base64.b64encode(
            buffer.getvalue()
        ).decode("ascii")

        return f"data:image/png;base64,{encoded_image}"