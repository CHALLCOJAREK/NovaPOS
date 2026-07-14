from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.report import (
    CashReportSchema,
    CustomersReportSchema,
    DebtsReportSchema,
    InventoryReportSchema,
    ProductsReportSchema,
    PurchasesReportSchema,
    SalesReportSchema,
    SuppliersReportSchema,
)
from app.services.report_service import ReportService


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


def _raise_invalid_period_error(error: ValueError) -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(error),
    ) from error


@router.get(
    "/sales",
    response_model=SalesReportSchema,
    summary="Obtener reporte de ventas",
)
def get_sales_report(
    start_date: date | None = Query(
        default=None,
        description="Fecha inicial del reporte.",
    ),
    end_date: date | None = Query(
        default=None,
        description="Fecha final del reporte.",
    ),
    db: Session = Depends(get_db),
) -> SalesReportSchema:
    try:
        return ReportService.get_sales_report(
            db=db,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as error:
        _raise_invalid_period_error(error)


@router.get(
    "/purchases",
    response_model=PurchasesReportSchema,
    summary="Obtener reporte de compras",
)
def get_purchases_report(
    start_date: date | None = Query(
        default=None,
        description="Fecha inicial del reporte.",
    ),
    end_date: date | None = Query(
        default=None,
        description="Fecha final del reporte.",
    ),
    db: Session = Depends(get_db),
) -> PurchasesReportSchema:
    try:
        return ReportService.get_purchases_report(
            db=db,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as error:
        _raise_invalid_period_error(error)


@router.get(
    "/inventory",
    response_model=InventoryReportSchema,
    summary="Obtener reporte de inventario",
)
def get_inventory_report(
    db: Session = Depends(get_db),
) -> InventoryReportSchema:
    return ReportService.get_inventory_report(db=db)


@router.get(
    "/cash",
    response_model=CashReportSchema,
    summary="Obtener reporte de caja",
)
def get_cash_report(
    start_date: date | None = Query(
        default=None,
        description="Fecha inicial del reporte.",
    ),
    end_date: date | None = Query(
        default=None,
        description="Fecha final del reporte.",
    ),
    db: Session = Depends(get_db),
) -> CashReportSchema:
    try:
        return ReportService.get_cash_report(
            db=db,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as error:
        _raise_invalid_period_error(error)


@router.get(
    "/customers",
    response_model=CustomersReportSchema,
    summary="Obtener reporte de clientes",
)
def get_customers_report(
    db: Session = Depends(get_db),
) -> CustomersReportSchema:
    return ReportService.get_customers_report(db=db)


@router.get(
    "/debts",
    response_model=DebtsReportSchema,
    summary="Obtener reporte de fiados",
)
def get_debts_report(
    start_date: date | None = Query(
        default=None,
        description="Fecha inicial del reporte.",
    ),
    end_date: date | None = Query(
        default=None,
        description="Fecha final del reporte.",
    ),
    db: Session = Depends(get_db),
) -> DebtsReportSchema:
    try:
        return ReportService.get_debts_report(
            db=db,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as error:
        _raise_invalid_period_error(error)


@router.get(
    "/products",
    response_model=ProductsReportSchema,
    summary="Obtener reporte de productos",
)
def get_products_report(
    db: Session = Depends(get_db),
) -> ProductsReportSchema:
    return ReportService.get_products_report(db=db)


@router.get(
    "/suppliers",
    response_model=SuppliersReportSchema,
    summary="Obtener reporte de proveedores",
)
def get_suppliers_report(
    db: Session = Depends(get_db),
) -> SuppliersReportSchema:
    return ReportService.get_suppliers_report(db=db)