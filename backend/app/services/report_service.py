from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.repositories.report_repository import ReportRepository
from app.schemas.report import (
    CashReportItemSchema,
    CashReportSchema,
    CustomerReportItemSchema,
    CustomersReportSchema,
    DebtReportItemSchema,
    DebtsReportSchema,
    InventoryReportItemSchema,
    InventoryReportSchema,
    ProductReportItemSchema,
    ProductsReportSchema,
    PurchaseReportItemSchema,
    PurchasesReportSchema,
    ReportPeriodSchema,
    SalesReportItemSchema,
    SalesReportSchema,
    SupplierReportItemSchema,
    SuppliersReportSchema,
)


class ReportService:
    """
    Lógica de negocio para los reportes comerciales de NovaPOS.

    Este servicio transforma los resultados del repository en respuestas
    Pydantic listas para ser expuestas mediante endpoints REST.
    """

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
    def _validate_period(
        start_date: date | None,
        end_date: date | None,
    ) -> None:
        if (
            start_date is not None
            and end_date is not None
            and start_date > end_date
        ):
            raise ValueError(
                "La fecha inicial no puede ser mayor que la fecha final"
            )

    @staticmethod
    def get_sales_report(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> SalesReportSchema:
        ReportService._validate_period(start_date, end_date)

        rows = ReportRepository.get_sales_report(
            db=db,
            start_date=start_date,
            end_date=end_date,
        )

        items: list[SalesReportItemSchema] = []

        total_subtotal = Decimal("0.00")
        total_discounts = Decimal("0.00")
        total_sales_amount = Decimal("0.00")
        total_cost_amount = Decimal("0.00")
        total_profit_amount = Decimal("0.00")

        cash_sales_amount = Decimal("0.00")
        yape_sales_amount = Decimal("0.00")
        credit_sales_amount = Decimal("0.00")

        for row in rows:
            subtotal = ReportService._to_decimal(
                row["subtotal"]
            )
            discount_amount = ReportService._to_decimal(
                row["discount_amount"]
            )
            total_amount = ReportService._to_decimal(
                row["total_amount"]
            )
            total_cost = ReportService._to_decimal(
                row["total_cost"]
            )
            profit_amount = ReportService._to_decimal(
                row["profit_amount"]
            )

            payment_method = str(row["payment_method"]).upper()

            total_subtotal += subtotal
            total_discounts += discount_amount
            total_sales_amount += total_amount
            total_cost_amount += total_cost
            total_profit_amount += profit_amount

            if payment_method == "CASH":
                cash_sales_amount += total_amount
            elif payment_method == "YAPE":
                yape_sales_amount += total_amount
            elif payment_method == "CREDIT":
                credit_sales_amount += total_amount

            items.append(
                SalesReportItemSchema(
                    sale_id=row["sale_id"],
                    customer_id=row["customer_id"],
                    customer_name=row["customer_name"],
                    document_type=str(row["document_type"]),
                    payment_method=payment_method,
                    subtotal=subtotal,
                    discount_amount=discount_amount,
                    total_amount=total_amount,
                    total_cost=total_cost,
                    profit_amount=profit_amount,
                    items_quantity=ReportService._to_decimal(
                        row["items_quantity"],
                        default="0.000",
                    ),
                    is_confirmed=bool(row["is_confirmed"]),
                    created_at=row["created_at"],
                )
            )

        return SalesReportSchema(
            period=ReportPeriodSchema(
                start_date=start_date,
                end_date=end_date,
            ),
            total_sales_count=len(items),
            total_subtotal=total_subtotal,
            total_discounts=total_discounts,
            total_sales_amount=total_sales_amount,
            total_cost_amount=total_cost_amount,
            total_profit_amount=total_profit_amount,
            cash_sales_amount=cash_sales_amount,
            yape_sales_amount=yape_sales_amount,
            credit_sales_amount=credit_sales_amount,
            items=items,
        )

    @staticmethod
    def get_purchases_report(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> PurchasesReportSchema:
        ReportService._validate_period(start_date, end_date)

        rows = ReportRepository.get_purchases_report(
            db=db,
            start_date=start_date,
            end_date=end_date,
        )

        items: list[PurchaseReportItemSchema] = []

        total_subtotal = Decimal("0.00")
        total_tax_amount = Decimal("0.00")
        total_purchases_amount = Decimal("0.00")
        total_units = Decimal("0.000")

        for row in rows:
            subtotal = ReportService._to_decimal(
                row["subtotal"]
            )
            tax_amount = ReportService._to_decimal(
                row["tax_amount"]
            )
            total_amount = ReportService._to_decimal(
                row["total_amount"]
            )
            units = ReportService._to_decimal(
                row["total_units"],
                default="0.000",
            )

            total_subtotal += subtotal
            total_tax_amount += tax_amount
            total_purchases_amount += total_amount
            total_units += units

            items.append(
                PurchaseReportItemSchema(
                    purchase_id=row["purchase_id"],
                    supplier_id=row["supplier_id"],
                    supplier_name=row["supplier_name"],
                    document_type=(
                        str(row["document_type"])
                        if row["document_type"] is not None
                        else None
                    ),
                    document_number=row["document_number"],
                    purchase_date=row["purchase_date"],
                    subtotal=subtotal,
                    tax_amount=tax_amount,
                    total_amount=total_amount,
                    items_count=int(row["items_count"] or 0),
                    total_units=units,
                    is_confirmed=bool(row["is_confirmed"]),
                    created_at=row["created_at"],
                )
            )

        return PurchasesReportSchema(
            period=ReportPeriodSchema(
                start_date=start_date,
                end_date=end_date,
            ),
            total_purchases_count=len(items),
            total_subtotal=total_subtotal,
            total_tax_amount=total_tax_amount,
            total_purchases_amount=total_purchases_amount,
            total_units=total_units,
            items=items,
        )

    @staticmethod
    def get_inventory_report(
        db: Session,
    ) -> InventoryReportSchema:
        rows = ReportRepository.get_inventory_report(db=db)

        items: list[InventoryReportItemSchema] = []

        total_stock_quantity = Decimal("0.000")
        total_stock_cost_value = Decimal("0.00")
        total_stock_sale_value = Decimal("0.00")
        total_projected_profit = Decimal("0.00")

        low_stock_products_count = 0
        out_of_stock_products_count = 0
        expiring_products_count = 0

        today = date.today()

        for row in rows:
            stock = ReportService._to_decimal(
                row["stock"],
                default="0.000",
            )
            minimum_stock = ReportService._to_decimal(
                row["minimum_stock"],
                default="0.000",
            )
            stock_cost_value = ReportService._to_decimal(
                row["stock_cost_value"]
            )
            stock_sale_value = ReportService._to_decimal(
                row["stock_sale_value"]
            )
            projected_profit = ReportService._to_decimal(
                row["projected_profit"]
            )

            total_stock_quantity += stock
            total_stock_cost_value += stock_cost_value
            total_stock_sale_value += stock_sale_value
            total_projected_profit += projected_profit

            if stock <= Decimal("0"):
                out_of_stock_products_count += 1

            if stock <= minimum_stock:
                low_stock_products_count += 1

            expiration_date = row["expiration_date"]

            if (
                expiration_date is not None
                and stock > Decimal("0")
                and today <= expiration_date
                and (expiration_date - today).days <= 30
            ):
                expiring_products_count += 1

            items.append(
                InventoryReportItemSchema(
                    product_id=row["product_id"],
                    internal_code=row["internal_code"],
                    barcode=row["barcode"],
                    name=row["name"],
                    brand=row["brand"],
                    category_name=row["category_name"],
                    supplier_name=row["supplier_name"],
                    cost_price=ReportService._to_decimal(
                        row["cost_price"]
                    ),
                    sale_price=ReportService._to_decimal(
                        row["sale_price"]
                    ),
                    stock=stock,
                    minimum_stock=minimum_stock,
                    stock_cost_value=stock_cost_value,
                    stock_sale_value=stock_sale_value,
                    projected_profit=projected_profit,
                    expiration_date=expiration_date,
                    batch=row["batch"],
                    is_weighted=bool(row["is_weighted"]),
                    is_frozen=bool(row["is_frozen"]),
                    status=str(row["status"]),
                    is_active=bool(row["is_active"]),
                )
            )

        return InventoryReportSchema(
            total_products=len(items),
            total_stock_quantity=total_stock_quantity,
            total_stock_cost_value=total_stock_cost_value,
            total_stock_sale_value=total_stock_sale_value,
            total_projected_profit=total_projected_profit,
            low_stock_products_count=low_stock_products_count,
            out_of_stock_products_count=(
                out_of_stock_products_count
            ),
            expiring_products_count=expiring_products_count,
            items=items,
        )

    @staticmethod
    def get_cash_report(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> CashReportSchema:
        ReportService._validate_period(start_date, end_date)

        rows = ReportRepository.get_cash_report(
            db=db,
            start_date=start_date,
            end_date=end_date,
        )

        items: list[CashReportItemSchema] = []

        total_opening_amount = Decimal("0.00")
        total_cash_sales_amount = Decimal("0.00")
        total_yape_sales_amount = Decimal("0.00")
        total_credit_sales_amount = Decimal("0.00")
        total_manual_income_amount = Decimal("0.00")
        total_manual_expense_amount = Decimal("0.00")
        total_sales_amount = Decimal("0.00")
        total_profit_amount = Decimal("0.00")
        total_cash_difference_amount = Decimal("0.00")
        total_yape_difference_amount = Decimal("0.00")

        for row in rows:
            opening_amount = ReportService._to_decimal(
                row["opening_amount"]
            )
            cash_sales_amount = ReportService._to_decimal(
                row["cash_sales_amount"]
            )
            yape_sales_amount = ReportService._to_decimal(
                row["yape_sales_amount"]
            )
            credit_sales_amount = ReportService._to_decimal(
                row["credit_sales_amount"]
            )
            manual_income_amount = ReportService._to_decimal(
                row["manual_income_amount"]
            )
            manual_expense_amount = ReportService._to_decimal(
                row["manual_expense_amount"]
            )
            sales_amount = ReportService._to_decimal(
                row["total_sales_amount"]
            )
            profit_amount = ReportService._to_decimal(
                row["total_profit_amount"]
            )
            cash_difference = ReportService._to_decimal(
                row["cash_difference_amount"]
            )
            yape_difference = ReportService._to_decimal(
                row["yape_difference_amount"]
            )

            total_opening_amount += opening_amount
            total_cash_sales_amount += cash_sales_amount
            total_yape_sales_amount += yape_sales_amount
            total_credit_sales_amount += credit_sales_amount
            total_manual_income_amount += manual_income_amount
            total_manual_expense_amount += manual_expense_amount
            total_sales_amount += sales_amount
            total_profit_amount += profit_amount
            total_cash_difference_amount += cash_difference
            total_yape_difference_amount += yape_difference

            items.append(
                CashReportItemSchema(
                    cash_register_id=row["cash_register_id"],
                    opened_by_user_id=row["opened_by_user_id"],
                    closed_by_user_id=row["closed_by_user_id"],
                    opened_at=row["opened_at"],
                    closed_at=row["closed_at"],
                    opening_amount=opening_amount,
                    cash_sales_amount=cash_sales_amount,
                    yape_sales_amount=yape_sales_amount,
                    credit_sales_amount=credit_sales_amount,
                    manual_income_amount=manual_income_amount,
                    manual_expense_amount=manual_expense_amount,
                    expected_cash_amount=(
                        ReportService._to_decimal(
                            row["expected_cash_amount"]
                        )
                    ),
                    counted_cash_amount=(
                        ReportService._to_decimal(
                            row["counted_cash_amount"]
                        )
                        if row["counted_cash_amount"] is not None
                        else None
                    ),
                    cash_difference_amount=(
                        ReportService._to_decimal(
                            row["cash_difference_amount"]
                        )
                        if row["cash_difference_amount"] is not None
                        else None
                    ),
                    expected_yape_amount=(
                        ReportService._to_decimal(
                            row["expected_yape_amount"]
                        )
                    ),
                    confirmed_yape_amount=(
                        ReportService._to_decimal(
                            row["confirmed_yape_amount"]
                        )
                        if row["confirmed_yape_amount"] is not None
                        else None
                    ),
                    yape_difference_amount=(
                        ReportService._to_decimal(
                            row["yape_difference_amount"]
                        )
                        if row["yape_difference_amount"] is not None
                        else None
                    ),
                    total_sales_amount=sales_amount,
                    total_profit_amount=profit_amount,
                    status=str(row["status"]),
                )
            )

        return CashReportSchema(
            period=ReportPeriodSchema(
                start_date=start_date,
                end_date=end_date,
            ),
            total_registers=len(items),
            total_opening_amount=total_opening_amount,
            total_cash_sales_amount=total_cash_sales_amount,
            total_yape_sales_amount=total_yape_sales_amount,
            total_credit_sales_amount=total_credit_sales_amount,
            total_manual_income_amount=total_manual_income_amount,
            total_manual_expense_amount=total_manual_expense_amount,
            total_sales_amount=total_sales_amount,
            total_profit_amount=total_profit_amount,
            total_cash_difference_amount=(
                total_cash_difference_amount
            ),
            total_yape_difference_amount=(
                total_yape_difference_amount
            ),
            items=items,
        )

    @staticmethod
    def get_customers_report(
        db: Session,
    ) -> CustomersReportSchema:
        rows = ReportRepository.get_customers_report(db=db)

        items: list[CustomerReportItemSchema] = []

        active_customers = 0
        customers_with_purchases = 0
        customers_with_debt = 0
        total_purchased_amount = Decimal("0.00")
        total_pending_debt_amount = Decimal("0.00")

        for row in rows:
            purchased_amount = ReportService._to_decimal(
                row["total_purchased_amount"]
            )
            pending_debt_amount = ReportService._to_decimal(
                row["pending_debt_amount"]
            )
            purchases_count = int(row["purchases_count"] or 0)
            is_active = bool(row["is_active"])

            if is_active:
                active_customers += 1

            if purchases_count > 0:
                customers_with_purchases += 1

            if pending_debt_amount > Decimal("0"):
                customers_with_debt += 1

            total_purchased_amount += purchased_amount
            total_pending_debt_amount += pending_debt_amount

            items.append(
                CustomerReportItemSchema(
                    customer_id=row["customer_id"],
                    full_name=row["full_name"],
                    document_number=row["document_number"],
                    phone=row["phone"],
                    whatsapp=row["whatsapp"],
                    email=row["email"],
                    address=row["address"],
                    purchases_count=purchases_count,
                    total_purchased_amount=purchased_amount,
                    total_profit_generated=(
                        ReportService._to_decimal(
                            row["total_profit_generated"]
                        )
                    ),
                    total_credit_amount=(
                        ReportService._to_decimal(
                            row["total_credit_amount"]
                        )
                    ),
                    total_debt_paid_amount=(
                        ReportService._to_decimal(
                            row["total_debt_paid_amount"]
                        )
                    ),
                    pending_debt_amount=pending_debt_amount,
                    last_purchase_date=row["last_purchase_date"],
                    is_active=is_active,
                )
            )

        return CustomersReportSchema(
            total_customers=len(items),
            active_customers=active_customers,
            customers_with_purchases=customers_with_purchases,
            customers_with_debt=customers_with_debt,
            total_purchased_amount=total_purchased_amount,
            total_pending_debt_amount=(
                total_pending_debt_amount
            ),
            items=items,
        )

    @staticmethod
    def get_debts_report(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> DebtsReportSchema:
        ReportService._validate_period(start_date, end_date)

        rows = ReportRepository.get_debts_report(
            db=db,
            start_date=start_date,
            end_date=end_date,
        )

        items: list[DebtReportItemSchema] = []

        pending_debts = 0
        partial_debts = 0
        paid_debts = 0

        total_original_amount = Decimal("0.00")
        total_paid_amount = Decimal("0.00")
        total_pending_amount = Decimal("0.00")

        for row in rows:
            original_amount = ReportService._to_decimal(
                row["original_amount"]
            )
            paid_amount = ReportService._to_decimal(
                row["paid_amount"]
            )
            pending_amount = ReportService._to_decimal(
                row["pending_amount"]
            )

            status = str(row["status"]).upper()

            if status == "PENDING":
                pending_debts += 1
            elif status == "PARTIAL":
                partial_debts += 1
            elif status == "PAID":
                paid_debts += 1

            total_original_amount += original_amount
            total_paid_amount += paid_amount
            total_pending_amount += pending_amount

            items.append(
                DebtReportItemSchema(
                    debt_id=row["debt_id"],
                    sale_id=row["sale_id"],
                    customer_id=row["customer_id"],
                    customer_name=row["customer_name"],
                    original_amount=original_amount,
                    paid_amount=paid_amount,
                    pending_amount=pending_amount,
                    status=status,
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    payments_count=int(
                        row["payments_count"] or 0
                    ),
                    last_payment_date=row["last_payment_date"],
                )
            )

        return DebtsReportSchema(
            period=ReportPeriodSchema(
                start_date=start_date,
                end_date=end_date,
            ),
            total_debts=len(items),
            pending_debts=pending_debts,
            partial_debts=partial_debts,
            paid_debts=paid_debts,
            total_original_amount=total_original_amount,
            total_paid_amount=total_paid_amount,
            total_pending_amount=total_pending_amount,
            items=items,
        )

    @staticmethod
    def get_products_report(
        db: Session,
    ) -> ProductsReportSchema:
        rows = ReportRepository.get_products_report(db=db)

        items: list[ProductReportItemSchema] = []

        active_products = 0
        inactive_products = 0
        low_stock_products = 0
        products_with_sales = 0

        total_sold_quantity = Decimal("0.000")
        total_sales_amount = Decimal("0.00")
        total_generated_profit = Decimal("0.00")

        for row in rows:
            is_active = bool(row["is_active"])
            stock = ReportService._to_decimal(
                row["stock"],
                default="0.000",
            )
            minimum_stock = ReportService._to_decimal(
                row["minimum_stock"],
                default="0.000",
            )
            sold_quantity = ReportService._to_decimal(
                row["sold_quantity"],
                default="0.000",
            )
            sales_amount = ReportService._to_decimal(
                row["sales_amount"]
            )
            generated_profit = ReportService._to_decimal(
                row["generated_profit"]
            )

            if is_active:
                active_products += 1
            else:
                inactive_products += 1

            if stock <= minimum_stock:
                low_stock_products += 1

            if sold_quantity > Decimal("0"):
                products_with_sales += 1

            total_sold_quantity += sold_quantity
            total_sales_amount += sales_amount
            total_generated_profit += generated_profit

            items.append(
                ProductReportItemSchema(
                    product_id=row["product_id"],
                    internal_code=row["internal_code"],
                    barcode=row["barcode"],
                    name=row["name"],
                    brand=row["brand"],
                    category_name=row["category_name"],
                    supplier_name=row["supplier_name"],
                    cost_price=ReportService._to_decimal(
                        row["cost_price"]
                    ),
                    sale_price=ReportService._to_decimal(
                        row["sale_price"]
                    ),
                    profit_margin=ReportService._to_decimal(
                        row["profit_margin"]
                    ),
                    profit_amount=ReportService._to_decimal(
                        row["profit_amount"]
                    ),
                    stock=stock,
                    minimum_stock=minimum_stock,
                    sold_quantity=sold_quantity,
                    sales_amount=sales_amount,
                    generated_profit=generated_profit,
                    expiration_date=row["expiration_date"],
                    is_weighted=bool(row["is_weighted"]),
                    is_frozen=bool(row["is_frozen"]),
                    status=str(row["status"]),
                    is_active=is_active,
                )
            )

        return ProductsReportSchema(
            total_products=len(items),
            active_products=active_products,
            inactive_products=inactive_products,
            low_stock_products=low_stock_products,
            products_with_sales=products_with_sales,
            total_sold_quantity=total_sold_quantity,
            total_sales_amount=total_sales_amount,
            total_generated_profit=total_generated_profit,
            items=items,
        )

    @staticmethod
    def get_suppliers_report(
        db: Session,
    ) -> SuppliersReportSchema:
        rows = ReportRepository.get_suppliers_report(db=db)

        items: list[SupplierReportItemSchema] = []

        active_suppliers = 0
        suppliers_with_products = 0
        suppliers_with_purchases = 0
        total_purchased_amount = Decimal("0.00")

        for row in rows:
            is_active = bool(row["is_active"])
            products_count = int(row["products_count"] or 0)
            purchases_count = int(row["purchases_count"] or 0)
            purchased_amount = ReportService._to_decimal(
                row["total_purchased_amount"]
            )

            if is_active:
                active_suppliers += 1

            if products_count > 0:
                suppliers_with_products += 1

            if purchases_count > 0:
                suppliers_with_purchases += 1

            total_purchased_amount += purchased_amount

            items.append(
                SupplierReportItemSchema(
                    supplier_id=row["supplier_id"],
                    name=row["name"],
                    ruc=row["ruc"],
                    phone=row["phone"],
                    whatsapp=row["whatsapp"],
                    email=row["email"],
                    contact_name=row["contact_name"],
                    products_count=products_count,
                    purchases_count=purchases_count,
                    total_purchased_amount=purchased_amount,
                    last_purchase_date=row["last_purchase_date"],
                    is_active=is_active,
                )
            )

        return SuppliersReportSchema(
            total_suppliers=len(items),
            active_suppliers=active_suppliers,
            suppliers_with_products=suppliers_with_products,
            suppliers_with_purchases=suppliers_with_purchases,
            total_purchased_amount=total_purchased_amount,
            items=items,
        )