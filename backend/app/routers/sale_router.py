from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.sale import SaleCreate, SaleResponse
from app.services.sale_service import SaleService


router = APIRouter(
    prefix="/sales",
    tags=["Sales"]
)


service = SaleService()


@router.post(
    "/",
    response_model=SaleResponse,
    status_code=201
)
def create_sale(
    data: SaleCreate,
    db: Session = Depends(get_db)
):

    return service.create_sale(
        db,
        data
    )


@router.get(
    "/",
    response_model=list[SaleResponse]
)
def get_sales(
    db: Session = Depends(get_db)
):

    return service.repository.get_all(
        db
    )


@router.get(
    "/{sale_id}",
    response_model=SaleResponse
)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db)
):

    sale = service.repository.get_by_id(
        db,
        sale_id
    )

    if not sale:
        raise HTTPException(
            status_code=404,
            detail="Venta no encontrada"
        )

    return sale


@router.delete(
    "/{sale_id}",
    response_model=SaleResponse
)
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db)
):

    sale = service.repository.get_by_id(
        db,
        sale_id
    )

    if not sale:
        raise HTTPException(
            status_code=404,
            detail="Venta no encontrada"
        )

    return service.repository.soft_delete(
        db,
        sale
    )