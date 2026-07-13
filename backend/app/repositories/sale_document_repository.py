from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.sale_document import SaleDocument
from app.schemas.sale_document_schema import (
    SaleDocumentCreate,
    SaleDocumentPathsUpdate,
)


class SaleDocumentRepository:
    @staticmethod
    def create(
        db: Session,
        document_data: SaleDocumentCreate,
    ) -> SaleDocument:
        document = SaleDocument(**document_data.model_dump())

        db.add(document)
        db.flush()
        db.refresh(document)

        return document

    @staticmethod
    def get_all(
        db: Session,
    ) -> list[SaleDocument]:
        statement = (
            select(SaleDocument)
            .where(SaleDocument.is_deleted.is_(False))
            .order_by(SaleDocument.id.desc())
        )

        return list(db.scalars(statement).all())

    @staticmethod
    def get_by_id(
        db: Session,
        document_id: int,
    ) -> SaleDocument | None:
        statement = select(SaleDocument).where(
            SaleDocument.id == document_id,
            SaleDocument.is_deleted.is_(False),
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_sale_id(
        db: Session,
        sale_id: int,
    ) -> SaleDocument | None:
        statement = select(SaleDocument).where(
            SaleDocument.sale_id == sale_id,
            SaleDocument.is_deleted.is_(False),
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_full_number(
        db: Session,
        full_number: str,
    ) -> SaleDocument | None:
        statement = select(SaleDocument).where(
            SaleDocument.full_number == full_number,
            SaleDocument.is_deleted.is_(False),
        )

        return db.scalar(statement)

    @staticmethod
    def get_next_number(
        db: Session,
        document_type: str,
        serie: str,
    ) -> int:
        statement = select(
            func.coalesce(func.max(SaleDocument.number), 0)
        ).where(
            SaleDocument.document_type == document_type,
            SaleDocument.serie == serie,
        )

        current_number = db.scalar(statement) or 0

        return int(current_number) + 1

    @staticmethod
    def update_paths(
        db: Session,
        document: SaleDocument,
        paths_data: SaleDocumentPathsUpdate,
    ) -> SaleDocument:
        update_data = paths_data.model_dump(exclude_unset=True)

        for field_name, value in update_data.items():
            setattr(document, field_name, value)

        db.add(document)
        db.flush()
        db.refresh(document)

        return document