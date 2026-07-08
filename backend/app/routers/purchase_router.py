from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.purchase import PurchaseCreate, PurchaseResponse
from app.services.purchase_service import PurchaseService


router = APIRouter(
    prefix="/purchases",
    tags=["Purchases"],
)


@router.get(
    "/",
    response_model=list[PurchaseResponse],
)
def get_purchases(
    db: Session = Depends(get_db),
):
    service = PurchaseService(db)
    return service.get_all()


@router.post(
    "/",
    response_model=PurchaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_purchase(
    data: PurchaseCreate,
    db: Session = Depends(get_db),
):
    service = PurchaseService(db)
    return service.create(data)


@router.get(
    "/{purchase_id}",
    response_model=PurchaseResponse,
)
def get_purchase_by_id(
    purchase_id: int,
    db: Session = Depends(get_db),
):
    service = PurchaseService(db)
    return service.get_by_id(purchase_id)


@router.delete(
    "/{purchase_id}",
    response_model=PurchaseResponse,
)
def delete_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
):
    service = PurchaseService(db)
    return service.delete(purchase_id)