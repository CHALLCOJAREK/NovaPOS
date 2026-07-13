from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.sale_document_schema import (
    SaleDocumentDownloadInfo,
    SaleDocumentResponse,
)
from app.services.sale_document_service import SaleDocumentService


router = APIRouter(
    prefix="/sale-documents",
    tags=["Sale Documents"],
)


@router.get(
    "/",
    response_model=list[SaleDocumentResponse],
)
def get_sale_documents(
    db: Session = Depends(get_db),
):
    return SaleDocumentService.get_all(
        db=db,
    )


@router.get(
    "/sale/{sale_id}",
    response_model=SaleDocumentResponse,
)
def get_sale_document_by_sale(
    sale_id: int,
    db: Session = Depends(get_db),
):
    return SaleDocumentService.get_by_sale_id(
        db=db,
        sale_id=sale_id,
    )


@router.get(
    "/{document_id}/download-info",
    response_model=SaleDocumentDownloadInfo,
)
def get_sale_document_download_info(
    document_id: int,
    db: Session = Depends(get_db),
):
    return SaleDocumentService.get_download_info(
        db=db,
        document_id=document_id,
    )


@router.post(
    "/{document_id}/regenerate",
    response_model=SaleDocumentResponse,
)
def regenerate_sale_document_files(
    document_id: int,
    db: Session = Depends(get_db),
):
    return SaleDocumentService.regenerate_document_files(
        db=db,
        document_id=document_id,
    )


@router.get(
    "/{document_id}",
    response_model=SaleDocumentResponse,
)
def get_sale_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    return SaleDocumentService.get_by_id(
        db=db,
        document_id=document_id,
    )