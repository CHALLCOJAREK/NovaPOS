from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.sale import Sale
from app.models.sale_document import SaleDocument
from app.models.store_setting import StoreSetting
from app.services.document_qr_service import DocumentQrService
from app.services.store_setting_service import StoreSettingService
from app.models.sale_item import SaleItem

class SaleReceiptContextService:
    MONEY_QUANTIZER = Decimal("0.01")
    QUANTITY_QUANTIZER = Decimal("0.001")

    PAYMENT_METHOD_LABELS = {
        "CASH": "EFECTIVO",
        "YAPE": "YAPE",
        "CREDIT": "FIADO",
    }

    DOCUMENT_TYPE_LABELS = {
        "NOTA_VENTA": "Nota de Venta",
        "BOLETA": "Boleta",
    }

    @classmethod
    def build_context(
        cls,
        db: Session,
        sale_id: int,
        document_id: int,
    ) -> dict:
        sale = cls._get_sale(
            db=db,
            sale_id=sale_id,
        )

        document = cls._get_document(
            db=db,
            document_id=document_id,
            sale_id=sale_id,
        )

        store_setting = cls._get_store_setting(db)

        issued_at = document.created_at or sale.created_at or datetime.now()

        qr_result = DocumentQrService.generate(
            full_number=document.full_number,
            sale_id=sale.id,
            issued_at=issued_at,
            total_amount=Decimal(str(document.total_amount)),
        )

        customer_name = "Cliente general"
        customer_document = "Sin documento"

        if sale.customer is not None:
            customer_name = (
                sale.customer.full_name
                or "Cliente general"
            )

            customer_document = (
                sale.customer.document_number
                or "Sin documento"
            )

        items = []

        for sale_item in sale.items:
            product_name = "Producto"

            if sale_item.product is not None:
                product_name = sale_item.product.name

                if sale_item.product.brand:
                    product_name = (
                        f"{product_name} "
                        f"{sale_item.product.brand}"
                    )

            items.append(
                {
                    "description": product_name,
                    "quantity": cls._format_quantity(
                        sale_item.quantity
                    ),
                    "unit_price": cls._format_money(
                        sale_item.unit_price
                    ),
                    "total": cls._format_money(
                        sale_item.subtotal
                    ),
                }
            )

        document_type = str(document.document_type).upper()

        tax_percentage = (
            "18"
            if document_type == "BOLETA"
            else "0"
        )

        return {
            "store": {
                "logo_uri": StoreSettingService.get_logo_uri(
                    store_setting.logo_path
                ),
                "store_name": (
                    store_setting.store_name
                    or "Tienda de Abarrotes Danae"
                ),
                "business_name": (
                    store_setting.business_name
                    or store_setting.store_name
                    or "Tienda de Abarrotes Danae"
                ),
                "tagline": "Calidad y confianza para tu hogar",
                "ruc": (
                    store_setting.ruc
                    or "10765432109"
                ),
                "address": (
                    store_setting.address
                    or (
                        "San José de Media Luna, "
                        "Urubamba - Cusco - Perú"
                    )
                ),
                "whatsapp": (
                    store_setting.whatsapp
                    or "987 018 591"
                ),
                "phone": (
                    store_setting.phone
                    or "(084) 123 456"
                ),
            },
            "document": {
                "display_type": cls.DOCUMENT_TYPE_LABELS.get(
                    document_type,
                    document_type.replace("_", " ").title(),
                ),
                "full_number": document.full_number,
                "issue_date": issued_at.strftime("%d/%m/%Y"),
                "issue_time": issued_at.strftime("%H:%M"),
                "cashier_name": "Sistema NovaPOS",
                "subtotal": cls._format_money(
                    document.subtotal
                ),
                "tax_percentage": tax_percentage,
                "tax_amount": cls._format_money(
                    document.tax_amount
                ),
                "total_amount": cls._format_money(
                    document.total_amount
                ),
            },
            "customer": {
                "name": customer_name,
                "document_number": customer_document,
            },
            "payment_method": cls.PAYMENT_METHOD_LABELS.get(
                str(sale.payment_method).upper(),
                str(sale.payment_method).replace("_", " ").title(),
            ),
            "items": items,
            "qr": {
                "image_uri": qr_result.image_uri,
                "content": qr_result.content,
            },
        }

    @staticmethod
    def _get_sale(
        db: Session,
        sale_id: int,
    ) -> Sale:
        sale = (
            db.query(Sale)
            .options(
                joinedload(Sale.customer),
                joinedload(Sale.items).joinedload(SaleItem.product),
            )
            .filter(
                Sale.id == sale_id,
                Sale.is_deleted == False,
            )
            .first()
        )

        if sale is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venta no encontrada",
            )

        return sale

    @staticmethod
    def _get_document(
        db: Session,
        document_id: int,
        sale_id: int,
    ) -> SaleDocument:
        document = (
            db.query(SaleDocument)
            .filter(
                SaleDocument.id == document_id,
                SaleDocument.sale_id == sale_id,
                SaleDocument.is_deleted == False,
            )
            .first()
        )

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comprobante no encontrado para la venta",
            )

        return document

    @staticmethod
    def _get_store_setting(
        db: Session,
    ) -> StoreSetting:
        store_setting = (
            db.query(StoreSetting)
            .filter(
                StoreSetting.is_active == True,
                StoreSetting.is_deleted == False,
            )
            .first()
        )

        if store_setting is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuración de tienda no encontrada",
            )

        return store_setting

    @classmethod
    def _format_money(
        cls,
        value: Decimal,
    ) -> str:
        normalized_value = Decimal(str(value)).quantize(
            cls.MONEY_QUANTIZER,
            rounding=ROUND_HALF_UP,
        )

        return f"{normalized_value:.2f}"

    @classmethod
    def _format_quantity(
        cls,
        value: Decimal,
    ) -> str:
        normalized_value = Decimal(str(value)).quantize(
            cls.QUANTITY_QUANTIZER,
            rounding=ROUND_HALF_UP,
        )

        formatted_value = format(
            normalized_value,
            "f",
        ).rstrip("0").rstrip(".")

        return formatted_value or "0"