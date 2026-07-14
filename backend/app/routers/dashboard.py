from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dashboard import (
    DashboardCustomerDebtsResponseSchema,
    DashboardExpiringProductsResponseSchema,
    DashboardPurchaseSuggestionsResponseSchema,
    DashboardRecentSalesResponseSchema,
    DashboardStockAlertsResponseSchema,
    DashboardSummarySchema,
    DashboardTopProductsResponseSchema,
)
from app.services.dashboard_service import DashboardService


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/summary",
    response_model=DashboardSummarySchema,
    summary="Obtener resumen comercial",
)
def get_dashboard_summary(
    target_date: date | None = Query(
        default=None,
        description=(
            "Fecha del resumen comercial. "
            "Si no se envía, se utiliza la fecha actual."
        ),
    ),
    expiration_days: int = Query(
        default=30,
        ge=0,
        le=365,
        description=(
            "Cantidad de días para considerar productos "
            "próximos a vencer."
        ),
    ),
    db: Session = Depends(get_db),
) -> DashboardSummarySchema:
    return DashboardService.get_summary(
        db=db,
        target_date=target_date,
        expiration_days=expiration_days,
    )


@router.get(
    "/top-products",
    response_model=DashboardTopProductsResponseSchema,
    summary="Obtener productos más vendidos",
)
def get_top_products(
    start_date: date | None = Query(
        default=None,
        description="Fecha inicial opcional.",
    ),
    end_date: date | None = Query(
        default=None,
        description="Fecha final opcional.",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Cantidad máxima de productos.",
    ),
    db: Session = Depends(get_db),
) -> DashboardTopProductsResponseSchema:
    return DashboardService.get_top_products(
        db=db,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )


@router.get(
    "/recent-sales",
    response_model=DashboardRecentSalesResponseSchema,
    summary="Obtener últimas ventas",
)
def get_recent_sales(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Cantidad máxima de ventas.",
    ),
    db: Session = Depends(get_db),
) -> DashboardRecentSalesResponseSchema:
    return DashboardService.get_recent_sales(
        db=db,
        limit=limit,
    )


@router.get(
    "/stock-alerts",
    response_model=DashboardStockAlertsResponseSchema,
    summary="Obtener productos con stock bajo",
)
def get_stock_alerts(
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
        description="Cantidad máxima de productos.",
    ),
    db: Session = Depends(get_db),
) -> DashboardStockAlertsResponseSchema:
    return DashboardService.get_stock_alerts(
        db=db,
        limit=limit,
    )


@router.get(
    "/expiring-products",
    response_model=DashboardExpiringProductsResponseSchema,
    summary="Obtener productos próximos a vencer",
)
def get_expiring_products(
    target_date: date | None = Query(
        default=None,
        description=(
            "Fecha base para calcular los vencimientos. "
            "Si no se envía, se utiliza la fecha actual."
        ),
    ),
    days: int = Query(
        default=30,
        ge=0,
        le=365,
        description="Rango máximo de días hasta el vencimiento.",
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
        description="Cantidad máxima de productos.",
    ),
    db: Session = Depends(get_db),
) -> DashboardExpiringProductsResponseSchema:
    return DashboardService.get_expiring_products(
        db=db,
        target_date=target_date,
        days=days,
        limit=limit,
    )


@router.get(
    "/purchase-suggestions",
    response_model=DashboardPurchaseSuggestionsResponseSchema,
    summary="Obtener productos sugeridos para comprar",
)
def get_purchase_suggestions(
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
        description="Cantidad máxima de productos.",
    ),
    db: Session = Depends(get_db),
) -> DashboardPurchaseSuggestionsResponseSchema:
    return DashboardService.get_purchase_suggestions(
        db=db,
        limit=limit,
    )


@router.get(
    "/customer-debts",
    response_model=DashboardCustomerDebtsResponseSchema,
    summary="Obtener clientes con deuda",
)
def get_customer_debts(
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
        description="Cantidad máxima de clientes.",
    ),
    db: Session = Depends(get_db),
) -> DashboardCustomerDebtsResponseSchema:
    return DashboardService.get_customer_debts(
        db=db,
        limit=limit,
    )