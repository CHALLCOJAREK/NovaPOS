from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DashboardBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DashboardSummarySchema(DashboardBaseSchema):
    report_date: date

    daily_sales_amount: Decimal = Field(default=Decimal("0.00"))
    daily_purchases_amount: Decimal = Field(default=Decimal("0.00"))
    daily_profit_amount: Decimal = Field(default=Decimal("0.00"))

    current_cash_register_id: int | None = None
    current_cash_register_status: str | None = None

    cash_amount: Decimal = Field(default=Decimal("0.00"))
    yape_amount: Decimal = Field(default=Decimal("0.00"))
    credit_amount: Decimal = Field(default=Decimal("0.00"))

    products_sold_quantity: Decimal = Field(default=Decimal("0.000"))

    low_stock_products_count: int = 0
    expiring_products_count: int = 0
    purchase_suggestions_count: int = 0
    customers_with_debt_count: int = 0

    total_pending_debt_amount: Decimal = Field(default=Decimal("0.00"))

    total_customers: int = 0
    total_suppliers: int = 0
    total_active_products: int = 0


class TopProductSchema(DashboardBaseSchema):
    product_id: int
    internal_code: str
    barcode: str | None = None
    name: str
    brand: str | None = None

    quantity_sold: Decimal = Field(default=Decimal("0.000"))
    sales_amount: Decimal = Field(default=Decimal("0.00"))
    profit_amount: Decimal = Field(default=Decimal("0.00"))


class RecentSaleSchema(DashboardBaseSchema):
    sale_id: int
    customer_id: int | None = None
    customer_name: str | None = None

    document_type: str
    document_number: str | None = None
    payment_method: str

    total_amount: Decimal = Field(default=Decimal("0.00"))
    profit_amount: Decimal = Field(default=Decimal("0.00"))

    created_at: datetime


class StockAlertSchema(DashboardBaseSchema):
    product_id: int
    internal_code: str
    barcode: str | None = None
    name: str
    brand: str | None = None

    current_stock: Decimal = Field(default=Decimal("0.000"))
    minimum_stock: Decimal = Field(default=Decimal("0.000"))
    missing_stock: Decimal = Field(default=Decimal("0.000"))

    status: str


class ExpiringProductSchema(DashboardBaseSchema):
    product_id: int
    internal_code: str
    barcode: str | None = None
    name: str
    brand: str | None = None

    stock: Decimal = Field(default=Decimal("0.000"))
    expiration_date: date
    batch: str | None = None

    days_until_expiration: int
    expiration_status: str


class PurchaseSuggestionSchema(DashboardBaseSchema):
    product_id: int
    internal_code: str
    barcode: str | None = None
    name: str
    brand: str | None = None

    current_stock: Decimal = Field(default=Decimal("0.000"))
    minimum_stock: Decimal = Field(default=Decimal("0.000"))
    suggested_quantity: Decimal = Field(default=Decimal("0.000"))

    supplier_id: int | None = None
    supplier_name: str | None = None

    reason: str


class CustomerDebtDashboardSchema(DashboardBaseSchema):
    customer_id: int
    customer_name: str
    document_number: str | None = None
    phone: str | None = None
    whatsapp: str | None = None

    total_debt_amount: Decimal = Field(default=Decimal("0.00"))
    total_paid_amount: Decimal = Field(default=Decimal("0.00"))
    pending_amount: Decimal = Field(default=Decimal("0.00"))

    pending_debts_count: int = 0
    oldest_debt_date: datetime | None = None
    last_payment_date: datetime | None = None


class DashboardTopProductsResponseSchema(DashboardBaseSchema):
    items: list[TopProductSchema]
    total: int


class DashboardRecentSalesResponseSchema(DashboardBaseSchema):
    items: list[RecentSaleSchema]
    total: int


class DashboardStockAlertsResponseSchema(DashboardBaseSchema):
    items: list[StockAlertSchema]
    total: int


class DashboardExpiringProductsResponseSchema(DashboardBaseSchema):
    items: list[ExpiringProductSchema]
    total: int


class DashboardPurchaseSuggestionsResponseSchema(DashboardBaseSchema):
    items: list[PurchaseSuggestionSchema]
    total: int


class DashboardCustomerDebtsResponseSchema(DashboardBaseSchema):
    items: list[CustomerDebtDashboardSchema]
    total: int
    total_pending_amount: Decimal = Field(default=Decimal("0.00"))