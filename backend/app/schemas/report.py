from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ReportBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ReportPeriodSchema(ReportBaseSchema):
    start_date: date | None = None
    end_date: date | None = None


class SalesReportItemSchema(ReportBaseSchema):
    sale_id: int
    customer_id: int | None = None
    customer_name: str | None = None

    document_type: str
    payment_method: str

    subtotal: Decimal = Field(default=Decimal("0.00"))
    discount_amount: Decimal = Field(default=Decimal("0.00"))
    total_amount: Decimal = Field(default=Decimal("0.00"))
    total_cost: Decimal = Field(default=Decimal("0.00"))
    profit_amount: Decimal = Field(default=Decimal("0.00"))

    items_quantity: Decimal = Field(default=Decimal("0.000"))

    is_confirmed: bool
    created_at: datetime


class SalesReportSchema(ReportBaseSchema):
    period: ReportPeriodSchema

    total_sales_count: int = 0
    total_subtotal: Decimal = Field(default=Decimal("0.00"))
    total_discounts: Decimal = Field(default=Decimal("0.00"))
    total_sales_amount: Decimal = Field(default=Decimal("0.00"))
    total_cost_amount: Decimal = Field(default=Decimal("0.00"))
    total_profit_amount: Decimal = Field(default=Decimal("0.00"))

    cash_sales_amount: Decimal = Field(default=Decimal("0.00"))
    yape_sales_amount: Decimal = Field(default=Decimal("0.00"))
    credit_sales_amount: Decimal = Field(default=Decimal("0.00"))

    items: list[SalesReportItemSchema]


class PurchaseReportItemSchema(ReportBaseSchema):
    purchase_id: int
    supplier_id: int | None = None
    supplier_name: str | None = None

    document_type: str | None = None
    document_number: str | None = None
    purchase_date: date

    subtotal: Decimal = Field(default=Decimal("0.00"))
    tax_amount: Decimal = Field(default=Decimal("0.00"))
    total_amount: Decimal = Field(default=Decimal("0.00"))

    items_count: int = 0
    total_units: Decimal = Field(default=Decimal("0.000"))

    is_confirmed: bool
    created_at: datetime


class PurchasesReportSchema(ReportBaseSchema):
    period: ReportPeriodSchema

    total_purchases_count: int = 0
    total_subtotal: Decimal = Field(default=Decimal("0.00"))
    total_tax_amount: Decimal = Field(default=Decimal("0.00"))
    total_purchases_amount: Decimal = Field(default=Decimal("0.00"))
    total_units: Decimal = Field(default=Decimal("0.000"))

    items: list[PurchaseReportItemSchema]


class InventoryReportItemSchema(ReportBaseSchema):
    product_id: int
    internal_code: str
    barcode: str | None = None
    name: str
    brand: str | None = None
    category_name: str | None = None
    supplier_name: str | None = None

    cost_price: Decimal = Field(default=Decimal("0.00"))
    sale_price: Decimal = Field(default=Decimal("0.00"))

    stock: Decimal = Field(default=Decimal("0.000"))
    minimum_stock: Decimal = Field(default=Decimal("0.000"))

    stock_cost_value: Decimal = Field(default=Decimal("0.00"))
    stock_sale_value: Decimal = Field(default=Decimal("0.00"))
    projected_profit: Decimal = Field(default=Decimal("0.00"))

    expiration_date: date | None = None
    batch: str | None = None

    is_weighted: bool
    is_frozen: bool
    status: str
    is_active: bool


class InventoryReportSchema(ReportBaseSchema):
    total_products: int = 0
    total_stock_quantity: Decimal = Field(default=Decimal("0.000"))
    total_stock_cost_value: Decimal = Field(default=Decimal("0.00"))
    total_stock_sale_value: Decimal = Field(default=Decimal("0.00"))
    total_projected_profit: Decimal = Field(default=Decimal("0.00"))

    low_stock_products_count: int = 0
    out_of_stock_products_count: int = 0
    expiring_products_count: int = 0

    items: list[InventoryReportItemSchema]


class CashReportItemSchema(ReportBaseSchema):
    cash_register_id: int
    opened_by_user_id: int | None = None
    closed_by_user_id: int | None = None

    opened_at: datetime
    closed_at: datetime | None = None

    opening_amount: Decimal = Field(default=Decimal("0.00"))
    cash_sales_amount: Decimal = Field(default=Decimal("0.00"))
    yape_sales_amount: Decimal = Field(default=Decimal("0.00"))
    credit_sales_amount: Decimal = Field(default=Decimal("0.00"))

    manual_income_amount: Decimal = Field(default=Decimal("0.00"))
    manual_expense_amount: Decimal = Field(default=Decimal("0.00"))

    expected_cash_amount: Decimal = Field(default=Decimal("0.00"))
    counted_cash_amount: Decimal | None = None
    cash_difference_amount: Decimal | None = None

    expected_yape_amount: Decimal = Field(default=Decimal("0.00"))
    confirmed_yape_amount: Decimal | None = None
    yape_difference_amount: Decimal | None = None

    total_sales_amount: Decimal = Field(default=Decimal("0.00"))
    total_profit_amount: Decimal = Field(default=Decimal("0.00"))

    status: str


class CashReportSchema(ReportBaseSchema):
    period: ReportPeriodSchema

    total_registers: int = 0
    total_opening_amount: Decimal = Field(default=Decimal("0.00"))
    total_cash_sales_amount: Decimal = Field(default=Decimal("0.00"))
    total_yape_sales_amount: Decimal = Field(default=Decimal("0.00"))
    total_credit_sales_amount: Decimal = Field(default=Decimal("0.00"))

    total_manual_income_amount: Decimal = Field(default=Decimal("0.00"))
    total_manual_expense_amount: Decimal = Field(default=Decimal("0.00"))

    total_sales_amount: Decimal = Field(default=Decimal("0.00"))
    total_profit_amount: Decimal = Field(default=Decimal("0.00"))
    total_cash_difference_amount: Decimal = Field(default=Decimal("0.00"))
    total_yape_difference_amount: Decimal = Field(default=Decimal("0.00"))

    items: list[CashReportItemSchema]


class CustomerReportItemSchema(ReportBaseSchema):
    customer_id: int
    full_name: str
    document_number: str | None = None
    phone: str | None = None
    whatsapp: str | None = None
    email: str | None = None
    address: str | None = None

    purchases_count: int = 0
    total_purchased_amount: Decimal = Field(default=Decimal("0.00"))
    total_profit_generated: Decimal = Field(default=Decimal("0.00"))

    total_credit_amount: Decimal = Field(default=Decimal("0.00"))
    total_debt_paid_amount: Decimal = Field(default=Decimal("0.00"))
    pending_debt_amount: Decimal = Field(default=Decimal("0.00"))

    last_purchase_date: datetime | None = None
    is_active: bool


class CustomersReportSchema(ReportBaseSchema):
    total_customers: int = 0
    active_customers: int = 0
    customers_with_purchases: int = 0
    customers_with_debt: int = 0

    total_purchased_amount: Decimal = Field(default=Decimal("0.00"))
    total_pending_debt_amount: Decimal = Field(default=Decimal("0.00"))

    items: list[CustomerReportItemSchema]


class DebtReportItemSchema(ReportBaseSchema):
    debt_id: int
    sale_id: int
    customer_id: int
    customer_name: str

    original_amount: Decimal = Field(default=Decimal("0.00"))
    paid_amount: Decimal = Field(default=Decimal("0.00"))
    pending_amount: Decimal = Field(default=Decimal("0.00"))

    status: str
    created_at: datetime
    updated_at: datetime

    payments_count: int = 0
    last_payment_date: datetime | None = None


class DebtsReportSchema(ReportBaseSchema):
    period: ReportPeriodSchema

    total_debts: int = 0
    pending_debts: int = 0
    partial_debts: int = 0
    paid_debts: int = 0

    total_original_amount: Decimal = Field(default=Decimal("0.00"))
    total_paid_amount: Decimal = Field(default=Decimal("0.00"))
    total_pending_amount: Decimal = Field(default=Decimal("0.00"))

    items: list[DebtReportItemSchema]


class ProductReportItemSchema(ReportBaseSchema):
    product_id: int
    internal_code: str
    barcode: str | None = None
    name: str
    brand: str | None = None
    category_name: str | None = None
    supplier_name: str | None = None

    cost_price: Decimal = Field(default=Decimal("0.00"))
    sale_price: Decimal = Field(default=Decimal("0.00"))
    profit_margin: Decimal = Field(default=Decimal("0.00"))
    profit_amount: Decimal = Field(default=Decimal("0.00"))

    stock: Decimal = Field(default=Decimal("0.000"))
    minimum_stock: Decimal = Field(default=Decimal("0.000"))

    sold_quantity: Decimal = Field(default=Decimal("0.000"))
    sales_amount: Decimal = Field(default=Decimal("0.00"))
    generated_profit: Decimal = Field(default=Decimal("0.00"))

    expiration_date: date | None = None
    is_weighted: bool
    is_frozen: bool
    status: str
    is_active: bool


class ProductsReportSchema(ReportBaseSchema):
    total_products: int = 0
    active_products: int = 0
    inactive_products: int = 0
    low_stock_products: int = 0
    products_with_sales: int = 0

    total_sold_quantity: Decimal = Field(default=Decimal("0.000"))
    total_sales_amount: Decimal = Field(default=Decimal("0.00"))
    total_generated_profit: Decimal = Field(default=Decimal("0.00"))

    items: list[ProductReportItemSchema]


class SupplierReportItemSchema(ReportBaseSchema):
    supplier_id: int
    name: str
    ruc: str | None = None
    phone: str | None = None
    whatsapp: str | None = None
    email: str | None = None
    contact_name: str | None = None

    products_count: int = 0
    purchases_count: int = 0

    total_purchased_amount: Decimal = Field(default=Decimal("0.00"))
    last_purchase_date: date | None = None

    is_active: bool


class SuppliersReportSchema(ReportBaseSchema):
    total_suppliers: int = 0
    active_suppliers: int = 0
    suppliers_with_products: int = 0
    suppliers_with_purchases: int = 0

    total_purchased_amount: Decimal = Field(default=Decimal("0.00"))

    items: list[SupplierReportItemSchema]