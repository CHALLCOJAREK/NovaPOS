from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.sale import Sale
from app.models.sale_document import SaleDocument
from app.repositories.sale_document_repository import SaleDocumentRepository
from app.schemas.sale_document_schema import (
    SaleDocumentCreate,
    SaleDocumentDownloadInfo,
    SaleDocumentPathsUpdate,
)
from app.services.document_html_service import DocumentHtmlService
from app.services.document_image_service import DocumentImageService
from app.services.document_pdf_service import DocumentPdfService
from app.services.sale_receipt_context_service import (
    SaleReceiptContextService,
)


class SaleDocumentService:
    BOLETA = "BOLETA"
    NOTA_VENTA = "NOTA_VENTA"

    BOLETA_SERIE = "B001"
    NOTA_VENTA_SERIE = "NV001"

    IGV_RATE = Decimal("0.18")
    IGV_DIVISOR = Decimal("1.18")
    MONEY_QUANTIZER = Decimal("0.01")

    @classmethod
    def get_all(
        cls,
        db: Session,
    ) -> list[SaleDocument]:
        return SaleDocumentRepository.get_all(db)

    @classmethod
    def get_by_id(
        cls,
        db: Session,
        document_id: int,
    ) -> SaleDocument:
        document = SaleDocumentRepository.get_by_id(
            db=db,
            document_id=document_id,
        )

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comprobante no encontrado",
            )

        return document

    @classmethod
    def get_by_sale_id(
        cls,
        db: Session,
        sale_id: int,
    ) -> SaleDocument:
        document = SaleDocumentRepository.get_by_sale_id(
            db=db,
            sale_id=sale_id,
        )

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La venta no tiene un comprobante generado",
            )

        return document

    @classmethod
    def create_for_sale(
        cls,
        db: Session,
        sale: Sale,
    ) -> SaleDocument:
        if sale.id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La venta debe estar registrada antes "
                    "de generar el comprobante"
                ),
            )

        document = SaleDocumentRepository.get_by_sale_id(
            db=db,
            sale_id=sale.id,
        )

        if document is None:
            document = cls._create_document_record(
                db=db,
                sale=sale,
            )

            try:
                db.commit()
                db.refresh(document)

            except Exception as exc:
                db.rollback()

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=(
                        "No se pudo guardar el registro "
                        "del comprobante"
                    ),
                ) from exc

        return cls.generate_document_files(
            db=db,
            document=document,
        )

    @classmethod
    def generate_document_files(
        cls,
        db: Session,
        document: SaleDocument,
    ) -> SaleDocument:
        if document.id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "El comprobante debe estar registrado antes "
                    "de generar archivos"
                ),
            )

        pdf_path = document.pdf_path
        image_path = document.image_path

        pdf_available = cls._file_exists(pdf_path)
        image_available = cls._file_exists(image_path)

        if pdf_available and image_available:
            return document

        generated_paths: list[str] = []

        try:
            context = SaleReceiptContextService.build_context(
                db=db,
                sale_id=document.sale_id,
                document_id=document.id,
            )

            html_content = DocumentHtmlService.render_sale_receipt(
                context=context,
            )

            if not pdf_available:
                pdf_path = DocumentPdfService.generate_from_html(
                    html_content=html_content,
                    full_number=document.full_number,
                )

                generated_paths.append(pdf_path)

            if not image_available:
                image_path = DocumentImageService.generate_from_html(
                    html_content=html_content,
                    full_number=document.full_number,
                )

                generated_paths.append(image_path)

            updated_document = cls.update_document_paths(
                db=db,
                document_id=document.id,
                pdf_path=pdf_path,
                image_path=image_path,
            )

            db.commit()
            db.refresh(updated_document)

            return updated_document

        except HTTPException:
            db.rollback()
            cls._remove_generated_files(generated_paths)
            raise

        except (
            ValueError,
            RuntimeError,
            OSError,
        ) as exc:
            db.rollback()
            cls._remove_generated_files(generated_paths)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "El comprobante fue registrado, pero no se pudieron "
                    "generar sus archivos PDF y PNG"
                ),
            ) from exc

        except Exception as exc:
            db.rollback()
            cls._remove_generated_files(generated_paths)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Ocurrió un error inesperado al generar "
                    "el comprobante"
                ),
            ) from exc

    @classmethod
    def regenerate_document_files(
        cls,
        db: Session,
        document_id: int,
    ) -> SaleDocument:
        document = cls.get_by_id(
            db=db,
            document_id=document_id,
        )

        return cls.generate_document_files(
            db=db,
            document=document,
        )

    @classmethod
    def update_document_paths(
        cls,
        db: Session,
        document_id: int,
        pdf_path: str | None,
        image_path: str | None,
    ) -> SaleDocument:
        document = cls.get_by_id(
            db=db,
            document_id=document_id,
        )

        paths_data = SaleDocumentPathsUpdate(
            pdf_path=pdf_path,
            image_path=image_path,
        )

        return SaleDocumentRepository.update_paths(
            db=db,
            document=document,
            paths_data=paths_data,
        )

    @classmethod
    def get_download_info(
        cls,
        db: Session,
        document_id: int,
    ) -> SaleDocumentDownloadInfo:
        document = cls.get_by_id(
            db=db,
            document_id=document_id,
        )

        return SaleDocumentDownloadInfo(
            id=document.id,
            sale_id=document.sale_id,
            document_type=document.document_type,
            full_number=document.full_number,
            pdf_path=document.pdf_path,
            image_path=document.image_path,
            pdf_available=cls._file_exists(document.pdf_path),
            image_available=cls._file_exists(document.image_path),
        )

    @classmethod
    def _create_document_record(
        cls,
        db: Session,
        sale: Sale,
    ) -> SaleDocument:
        document_type = cls._normalize_document_type(
            sale.document_type
        )

        serie = cls._get_serie(document_type)

        next_number = SaleDocumentRepository.get_next_number(
            db=db,
            document_type=document_type,
            serie=serie,
        )

        full_number = cls._build_full_number(
            serie=serie,
            number=next_number,
        )

        subtotal, tax_amount, total_amount = cls._calculate_totals(
            document_type=document_type,
            total_amount=Decimal(str(sale.total_amount)),
        )

        create_data = SaleDocumentCreate(
            sale_id=sale.id,
            document_type=document_type,
            serie=serie,
            number=next_number,
            full_number=full_number,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            pdf_path=None,
            image_path=None,
        )

        try:
            return SaleDocumentRepository.create(
                db=db,
                document_data=create_data,
            )

        except IntegrityError as exc:
            db.rollback()

            existing_document = SaleDocumentRepository.get_by_sale_id(
                db=db,
                sale_id=sale.id,
            )

            if existing_document is not None:
                return existing_document

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "No se pudo generar el correlativo del comprobante. "
                    "Intente emitir la venta nuevamente."
                ),
            ) from exc

    @classmethod
    def _normalize_document_type(
        cls,
        document_type: str,
    ) -> str:
        normalized_type = str(document_type).strip().upper()

        if normalized_type not in {
            cls.BOLETA,
            cls.NOTA_VENTA,
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de comprobante no válido",
            )

        return normalized_type

    @classmethod
    def _get_serie(
        cls,
        document_type: str,
    ) -> str:
        if document_type == cls.BOLETA:
            return cls.BOLETA_SERIE

        return cls.NOTA_VENTA_SERIE

    @classmethod
    def _build_full_number(
        cls,
        serie: str,
        number: int,
    ) -> str:
        return f"{serie}-{number:08d}"

    @classmethod
    def _calculate_totals(
        cls,
        document_type: str,
        total_amount: Decimal,
    ) -> tuple[Decimal, Decimal, Decimal]:
        normalized_total = cls._round_money(total_amount)

        if normalized_total < Decimal("0.00"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "El total del comprobante "
                    "no puede ser negativo"
                ),
            )

        if document_type == cls.BOLETA:
            subtotal = cls._round_money(
                normalized_total / cls.IGV_DIVISOR
            )

            tax_amount = cls._round_money(
                normalized_total - subtotal
            )

            return (
                subtotal,
                tax_amount,
                normalized_total,
            )

        return (
            normalized_total,
            Decimal("0.00"),
            normalized_total,
        )

    @classmethod
    def _round_money(
        cls,
        amount: Decimal,
    ) -> Decimal:
        return amount.quantize(
            cls.MONEY_QUANTIZER,
            rounding=ROUND_HALF_UP,
        )

    @staticmethod
    def _file_exists(
        file_path: str | None,
    ) -> bool:
        if not file_path:
            return False

        try:
            return Path(file_path).is_file()

        except OSError:
            return False

    @staticmethod
    def _remove_generated_files(
        generated_paths: list[str],
    ) -> None:
        for generated_path in generated_paths:
            try:
                file_path = Path(generated_path)

                if file_path.is_file():
                    file_path.unlink()

            except OSError:
                continue