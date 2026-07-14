from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import (
    CustomerDebtDashboardSchema,
    DashboardCustomerDebtsResponseSchema,
    DashboardExpiringProductsResponseSchema,
    DashboardPurchaseSuggestionsResponseSchema,
    DashboardRecentSalesResponseSchema,
    DashboardStockAlertsResponseSchema,
    DashboardSummarySchema,
    DashboardTopProductsResponseSchema,
    ExpiringProductSchema,
    PurchaseSuggestionSchema,
    RecentSaleSchema,
    StockAlertSchema,
    TopProductSchema,
)


class DashboardService:
    """
    Lógica comercial del Dashboard de NovaPOS.

    El servicio coordina las consultas del repository y transforma
    los resultados en schemas Pydantic listos para los endpoints REST.
    """

    DEFAULT_LIMIT = 10
    MAX_LIMIT = 100
    DEFAULT_EXPIRATION_DAYS = 30
    MAX_EXPIRATION_DAYS = 365

    @staticmethod
    def _to_decimal(
        value: Any,
        default: str = "0.00",
    ) -> Decimal:
        if value is None:
            return Decimal(default)

        if isinstance(value, Decimal):
            return value

        return Decimal(str(value))

    @staticmethod
    def _validate_limit(limit: int) -> int:
        if limit < 1:
            return 1

        if limit > DashboardService.MAX_LIMIT:
            return DashboardService.MAX_LIMIT

        return limit

    @staticmethod
    def _validate_expiration_days(days: int) -> int:
        if days < 0:
            return 0

        if days > DashboardService.MAX_EXPIRATION_DAYS:
            return DashboardService.MAX_EXPIRATION_DAYS

        return days

    @staticmethod
    def _get_expiration_status(
        days_until_expiration: int,
    ) -> str:
        if days_until_expiration < 0:
            return "EXPIRED"

        if days_until_expiration == 0:
            return "EXPIRES_TODAY"

        if days_until_expiration <= 7:
            return "CRITICAL"

        if days_until_expiration <= 15:
            return "WARNING"

        return "UPCOMING"

    @staticmethod
    def _get_stock_status(
        current_stock: Decimal,
        minimum_stock: Decimal,
    ) -> str:
        if current_stock <= Decimal("0"):
            return "OUT_OF_STOCK"

        if current_stock < minimum_stock:
            return "LOW_STOCK"

        return "MINIMUM_STOCK"

    @staticmethod
    def _get_purchase_reason(
        current_stock: Decimal,
        minimum_stock: Decimal,
    ) -> str:
        if current_stock <= Decimal("0"):
            return "Producto sin stock"

        if current_stock < minimum_stock:
            return "Stock por debajo del mínimo"

        return "Producto en stock mínimo"

    @staticmethod
    def get_summary(
        db: Session,
        target_date: date | None = None,
        expiration_days: int = DEFAULT_EXPIRATION_DAYS,
    ) -> DashboardSummarySchema:
        selected_date = target_date or date.today()
        validated_expiration_days = (
            DashboardService._validate_expiration_days(
                expiration_days
            )
        )

        expiration_end_date = (
            selected_date
            + timedelta(days=validated_expiration_days)
        )

        daily_sales = (
            DashboardRepository.get_daily_sales_summary(
                db=db,
                target_date=selected_date,
            )
        )

        daily_payment_totals = (
            DashboardRepository.get_daily_sales_by_payment_method(
                db=db,
                target_date=selected_date,
            )
        )

        daily_purchases_amount = (
            DashboardRepository.get_daily_purchases_amount(
                db=db,
                target_date=selected_date,
            )
        )

        products_sold_quantity = (
            DashboardRepository.get_daily_products_sold_quantity(
                db=db,
                target_date=selected_date,
            )
        )

        current_cash_register = (
            DashboardRepository.get_current_cash_register(db=db)
        )

        current_cash_register_id: int | None = None
        current_cash_register_status: str | None = None

        cash_amount = daily_payment_totals.get(
            "CASH",
            Decimal("0.00"),
        )
        yape_amount = daily_payment_totals.get(
            "YAPE",
            Decimal("0.00"),
        )
        credit_amount = daily_payment_totals.get(
            "CREDIT",
            Decimal("0.00"),
        )

        if current_cash_register is not None:
            current_cash_register_id = current_cash_register.id
            current_cash_register_status = getattr(
                current_cash_register,
                "status",
                "OPEN",
            )

            cash_amount = DashboardService._to_decimal(
                getattr(
                    current_cash_register,
                    "expected_cash_amount",
                    cash_amount,
                )
            )

            yape_amount = DashboardService._to_decimal(
                getattr(
                    current_cash_register,
                    "expected_yape_amount",
                    yape_amount,
                )
            )

            credit_amount = DashboardService._to_decimal(
                getattr(
                    current_cash_register,
                    "credit_sales_amount",
                    credit_amount,
                )
            )

        return DashboardSummarySchema(
            report_date=selected_date,
            daily_sales_amount=DashboardService._to_decimal(
                daily_sales.get("sales_amount")
            ),
            daily_purchases_amount=DashboardService._to_decimal(
                daily_purchases_amount
            ),
            daily_profit_amount=DashboardService._to_decimal(
                daily_sales.get("profit_amount")
            ),
            current_cash_register_id=current_cash_register_id,
            current_cash_register_status=(
                current_cash_register_status
            ),
            cash_amount=DashboardService._to_decimal(
                cash_amount
            ),
            yape_amount=DashboardService._to_decimal(
                yape_amount
            ),
            credit_amount=DashboardService._to_decimal(
                credit_amount
            ),
            products_sold_quantity=DashboardService._to_decimal(
                products_sold_quantity,
                default="0.000",
            ),
            low_stock_products_count=(
                DashboardRepository.count_low_stock_products(
                    db=db
                )
            ),
            expiring_products_count=(
                DashboardRepository.count_expiring_products(
                    db=db,
                    start_date=selected_date,
                    end_date=expiration_end_date,
                )
            ),
            purchase_suggestions_count=(
                DashboardRepository.count_purchase_suggestions(
                    db=db
                )
            ),
            customers_with_debt_count=(
                DashboardRepository.count_customers_with_debt(
                    db=db
                )
            ),
            total_pending_debt_amount=(
                DashboardRepository.get_total_pending_debt_amount(
                    db=db
                )
            ),
            total_customers=(
                DashboardRepository.count_customers(db=db)
            ),
            total_suppliers=(
                DashboardRepository.count_suppliers(db=db)
            ),
            total_active_products=(
                DashboardRepository.count_active_products(db=db)
            ),
        )

    @staticmethod
    def get_top_products(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = DEFAULT_LIMIT,
    ) -> DashboardTopProductsResponseSchema:
        validated_limit = DashboardService._validate_limit(limit)

        rows = DashboardRepository.get_top_products(
            db=db,
            start_date=start_date,
            end_date=end_date,
            limit=validated_limit,
        )

        items = [
            TopProductSchema(
                product_id=row["product_id"],
                internal_code=row["internal_code"],
                barcode=row["barcode"],
                name=row["name"],
                brand=row["brand"],
                quantity_sold=DashboardService._to_decimal(
                    row["quantity_sold"],
                    default="0.000",
                ),
                sales_amount=DashboardService._to_decimal(
                    row["sales_amount"]
                ),
                profit_amount=DashboardService._to_decimal(
                    row["profit_amount"]
                ),
            )
            for row in rows
        ]

        return DashboardTopProductsResponseSchema(
            items=items,
            total=len(items),
        )

    @staticmethod
    def get_recent_sales(
        db: Session,
        limit: int = DEFAULT_LIMIT,
    ) -> DashboardRecentSalesResponseSchema:
        validated_limit = DashboardService._validate_limit(limit)

        rows = DashboardRepository.get_recent_sales(
            db=db,
            limit=validated_limit,
        )

        items = [
            RecentSaleSchema(
                sale_id=row["sale_id"],
                customer_id=row["customer_id"],
                customer_name=row["customer_name"],
                document_type=str(row["document_type"]),
                document_number=row["document_number"],
                payment_method=str(row["payment_method"]),
                total_amount=DashboardService._to_decimal(
                    row["total_amount"]
                ),
                profit_amount=DashboardService._to_decimal(
                    row["profit_amount"]
                ),
                created_at=row["created_at"],
            )
            for row in rows
        ]

        return DashboardRecentSalesResponseSchema(
            items=items,
            total=len(items),
        )

    @staticmethod
    def get_stock_alerts(
        db: Session,
        limit: int = MAX_LIMIT,
    ) -> DashboardStockAlertsResponseSchema:
        validated_limit = DashboardService._validate_limit(limit)

        rows = DashboardRepository.get_stock_alerts(
            db=db,
            limit=validated_limit,
        )

        items: list[StockAlertSchema] = []

        for row in rows:
            current_stock = DashboardService._to_decimal(
                row["current_stock"],
                default="0.000",
            )
            minimum_stock = DashboardService._to_decimal(
                row["minimum_stock"],
                default="0.000",
            )

            missing_stock = minimum_stock - current_stock

            if missing_stock < Decimal("0"):
                missing_stock = Decimal("0.000")

            items.append(
                StockAlertSchema(
                    product_id=row["product_id"],
                    internal_code=row["internal_code"],
                    barcode=row["barcode"],
                    name=row["name"],
                    brand=row["brand"],
                    current_stock=current_stock,
                    minimum_stock=minimum_stock,
                    missing_stock=missing_stock,
                    status=DashboardService._get_stock_status(
                        current_stock=current_stock,
                        minimum_stock=minimum_stock,
                    ),
                )
            )

        return DashboardStockAlertsResponseSchema(
            items=items,
            total=len(items),
        )

    @staticmethod
    def get_expiring_products(
        db: Session,
        target_date: date | None = None,
        days: int = DEFAULT_EXPIRATION_DAYS,
        limit: int = MAX_LIMIT,
    ) -> DashboardExpiringProductsResponseSchema:
        selected_date = target_date or date.today()
        validated_days = (
            DashboardService._validate_expiration_days(days)
        )
        validated_limit = DashboardService._validate_limit(limit)

        end_date = selected_date + timedelta(
            days=validated_days
        )

        rows = DashboardRepository.get_expiring_products(
            db=db,
            start_date=selected_date,
            end_date=end_date,
            limit=validated_limit,
        )

        items: list[ExpiringProductSchema] = []

        for row in rows:
            expiration_date = row["expiration_date"]
            days_until_expiration = (
                expiration_date - selected_date
            ).days

            items.append(
                ExpiringProductSchema(
                    product_id=row["product_id"],
                    internal_code=row["internal_code"],
                    barcode=row["barcode"],
                    name=row["name"],
                    brand=row["brand"],
                    stock=DashboardService._to_decimal(
                        row["stock"],
                        default="0.000",
                    ),
                    expiration_date=expiration_date,
                    batch=row["batch"],
                    days_until_expiration=(
                        days_until_expiration
                    ),
                    expiration_status=(
                        DashboardService._get_expiration_status(
                            days_until_expiration
                        )
                    ),
                )
            )

        return DashboardExpiringProductsResponseSchema(
            items=items,
            total=len(items),
        )

    @staticmethod
    def get_purchase_suggestions(
        db: Session,
        limit: int = MAX_LIMIT,
    ) -> DashboardPurchaseSuggestionsResponseSchema:
        validated_limit = DashboardService._validate_limit(limit)

        rows = DashboardRepository.get_purchase_suggestions(
            db=db,
            limit=validated_limit,
        )

        items: list[PurchaseSuggestionSchema] = []

        for row in rows:
            current_stock = DashboardService._to_decimal(
                row["current_stock"],
                default="0.000",
            )
            minimum_stock = DashboardService._to_decimal(
                row["minimum_stock"],
                default="0.000",
            )

            suggested_quantity = minimum_stock - current_stock

            if suggested_quantity < Decimal("0"):
                suggested_quantity = Decimal("0.000")

            items.append(
                PurchaseSuggestionSchema(
                    product_id=row["product_id"],
                    internal_code=row["internal_code"],
                    barcode=row["barcode"],
                    name=row["name"],
                    brand=row["brand"],
                    current_stock=current_stock,
                    minimum_stock=minimum_stock,
                    suggested_quantity=suggested_quantity,
                    supplier_id=row["supplier_id"],
                    supplier_name=row["supplier_name"],
                    reason=DashboardService._get_purchase_reason(
                        current_stock=current_stock,
                        minimum_stock=minimum_stock,
                    ),
                )
            )

        return DashboardPurchaseSuggestionsResponseSchema(
            items=items,
            total=len(items),
        )

    @staticmethod
    def get_customer_debts(
        db: Session,
        limit: int = MAX_LIMIT,
    ) -> DashboardCustomerDebtsResponseSchema:
        validated_limit = DashboardService._validate_limit(limit)

        rows = DashboardRepository.get_customer_debts(
            db=db,
            limit=validated_limit,
        )

        items: list[CustomerDebtDashboardSchema] = []
        total_pending_amount = Decimal("0.00")

        for row in rows:
            pending_amount = DashboardService._to_decimal(
                row["pending_amount"]
            )

            total_pending_amount += pending_amount

            items.append(
                CustomerDebtDashboardSchema(
                    customer_id=row["customer_id"],
                    customer_name=row["customer_name"],
                    document_number=row["document_number"],
                    phone=row["phone"],
                    whatsapp=row["whatsapp"],
                    total_debt_amount=DashboardService._to_decimal(
                        row["total_debt_amount"]
                    ),
                    total_paid_amount=DashboardService._to_decimal(
                        row["total_paid_amount"]
                    ),
                    pending_amount=pending_amount,
                    pending_debts_count=int(
                        row["pending_debts_count"] or 0
                    ),
                    oldest_debt_date=row["oldest_debt_date"],
                    last_payment_date=None,
                )
            )

        return DashboardCustomerDebtsResponseSchema(
            items=items,
            total=len(items),
            total_pending_amount=total_pending_amount,
        )