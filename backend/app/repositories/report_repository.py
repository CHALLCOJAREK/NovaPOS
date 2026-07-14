from datetime import date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.cash_register import CashRegister
from app.models.customer import Customer
from app.models.customer_debt import CustomerDebt
from app.models.customer_debt_payment import CustomerDebtPayment
from app.models.product import Product
from app.models.product_category import ProductCategory
from app.models.purchase import Purchase
from app.models.purchase_item import PurchaseItem
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.supplier import Supplier


class ReportRepository:
    """
    Repository de consultas para los reportes comerciales de NovaPOS.

    Esta clase es el único punto de acceso SQLAlchemy para la Fase 14.
    No contiene lógica de presentación ni construye schemas Pydantic.
    """

    @staticmethod
    def _date_range(
        start_date: date | None,
        end_date: date | None,
    ) -> tuple[datetime | None, datetime | None]:
        start_datetime = (
            datetime.combine(start_date, time.min)
            if start_date is not None
            else None
        )

        end_datetime = (
            datetime.combine(
                end_date + timedelta(days=1),
                time.min,
            )
            if end_date is not None
            else None
        )

        return start_datetime, end_datetime

    @staticmethod
    def get_sales_report(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list:
        start_datetime, end_datetime = ReportRepository._date_range(
            start_date,
            end_date,
        )

        items_quantity_subquery = (
            select(
                SaleItem.sale_id.label("sale_id"),
                func.coalesce(
                    func.sum(SaleItem.quantity),
                    0,
                ).label("items_quantity"),
            )
            .group_by(SaleItem.sale_id)
            .subquery()
        )

        statement = (
            select(
                Sale.id.label("sale_id"),
                Sale.customer_id,
                Customer.full_name.label("customer_name"),
                Sale.document_type,
                Sale.payment_method,
                Sale.subtotal,
                Sale.discount_amount,
                Sale.total_amount,
                Sale.total_cost,
                Sale.profit_amount,
                func.coalesce(
                    items_quantity_subquery.c.items_quantity,
                    0,
                ).label("items_quantity"),
                Sale.is_confirmed,
                Sale.created_at,
            )
            .outerjoin(
                Customer,
                Customer.id == Sale.customer_id,
            )
            .outerjoin(
                items_quantity_subquery,
                items_quantity_subquery.c.sale_id == Sale.id,
            )
            .where(
                Sale.is_deleted.is_(False),
                Sale.is_confirmed.is_(True),
            )
        )

        if start_datetime is not None:
            statement = statement.where(
                Sale.created_at >= start_datetime
            )

        if end_datetime is not None:
            statement = statement.where(
                Sale.created_at < end_datetime
            )

        statement = statement.order_by(Sale.created_at.desc())

        return list(db.execute(statement).mappings().all())

    @staticmethod
    def get_purchases_report(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list:
        item_totals_subquery = (
            select(
                PurchaseItem.purchase_id.label("purchase_id"),
                func.count(PurchaseItem.id).label("items_count"),
                func.coalesce(
                    func.sum(PurchaseItem.unit_quantity),
                    0,
                ).label("total_units"),
            )
            .where(PurchaseItem.is_deleted.is_(False))
            .group_by(PurchaseItem.purchase_id)
            .subquery()
        )

        statement = (
            select(
                Purchase.id.label("purchase_id"),
                Purchase.supplier_id,
                Supplier.name.label("supplier_name"),
                Purchase.document_type,
                Purchase.document_number,
                Purchase.purchase_date,
                Purchase.subtotal,
                Purchase.tax_amount,
                Purchase.total_amount,
                func.coalesce(
                    item_totals_subquery.c.items_count,
                    0,
                ).label("items_count"),
                func.coalesce(
                    item_totals_subquery.c.total_units,
                    0,
                ).label("total_units"),
                Purchase.is_confirmed,
                Purchase.created_at,
            )
            .outerjoin(
                Supplier,
                Supplier.id == Purchase.supplier_id,
            )
            .outerjoin(
                item_totals_subquery,
                item_totals_subquery.c.purchase_id == Purchase.id,
            )
            .where(
                Purchase.is_deleted.is_(False),
                Purchase.is_confirmed.is_(True),
            )
        )

        if start_date is not None:
            statement = statement.where(
                Purchase.purchase_date >= start_date
            )

        if end_date is not None:
            statement = statement.where(
                Purchase.purchase_date <= end_date
            )

        statement = statement.order_by(
            Purchase.purchase_date.desc(),
            Purchase.created_at.desc(),
        )

        return list(db.execute(statement).mappings().all())

    @staticmethod
    def get_inventory_report(
        db: Session,
    ) -> list:
        stock_cost_value = Product.stock * Product.cost_price
        stock_sale_value = Product.stock * Product.sale_price
        projected_profit = (
            Product.stock
            * (Product.sale_price - Product.cost_price)
        )

        statement = (
            select(
                Product.id.label("product_id"),
                Product.internal_code,
                Product.barcode,
                Product.name,
                Product.brand,
                ProductCategory.name.label("category_name"),
                Supplier.name.label("supplier_name"),
                Product.cost_price,
                Product.sale_price,
                Product.stock,
                Product.minimum_stock,
                stock_cost_value.label("stock_cost_value"),
                stock_sale_value.label("stock_sale_value"),
                projected_profit.label("projected_profit"),
                Product.expiration_date,
                Product.batch,
                Product.is_weighted,
                Product.is_frozen,
                Product.status,
                Product.is_active,
            )
            .outerjoin(
                ProductCategory,
                ProductCategory.id == Product.category_id,
            )
            .outerjoin(
                Supplier,
                Supplier.id == Product.supplier_id,
            )
            .where(Product.is_deleted.is_(False))
            .order_by(Product.name.asc())
        )

        return list(db.execute(statement).mappings().all())

    @staticmethod
    def get_cash_report(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list:
        start_datetime, end_datetime = ReportRepository._date_range(
            start_date,
            end_date,
        )

        statement = select(
            CashRegister.id.label("cash_register_id"),
            CashRegister.opened_by_user_id,
            CashRegister.closed_by_user_id,
            CashRegister.opened_at,
            CashRegister.closed_at,
            CashRegister.opening_amount,
            CashRegister.cash_sales_amount,
            CashRegister.yape_sales_amount,
            CashRegister.credit_sales_amount,
            CashRegister.manual_income_amount,
            CashRegister.manual_expense_amount,
            CashRegister.expected_cash_amount,
            CashRegister.counted_cash_amount,
            CashRegister.cash_difference_amount,
            CashRegister.expected_yape_amount,
            CashRegister.confirmed_yape_amount,
            CashRegister.yape_difference_amount,
            CashRegister.total_sales_amount,
            CashRegister.total_profit_amount,
            CashRegister.status,
        ).where(CashRegister.is_deleted.is_(False))

        if start_datetime is not None:
            statement = statement.where(
                CashRegister.opened_at >= start_datetime
            )

        if end_datetime is not None:
            statement = statement.where(
                CashRegister.opened_at < end_datetime
            )

        statement = statement.order_by(
            CashRegister.opened_at.desc()
        )

        return list(db.execute(statement).mappings().all())

    @staticmethod
    def get_customers_report(
        db: Session,
    ) -> list:
        sales_subquery = (
            select(
                Sale.customer_id.label("customer_id"),
                func.count(Sale.id).label("purchases_count"),
                func.coalesce(
                    func.sum(Sale.total_amount),
                    0,
                ).label("total_purchased_amount"),
                func.coalesce(
                    func.sum(Sale.profit_amount),
                    0,
                ).label("total_profit_generated"),
                func.max(Sale.created_at).label(
                    "last_purchase_date"
                ),
            )
            .where(
                Sale.customer_id.is_not(None),
                Sale.is_confirmed.is_(True),
                Sale.is_deleted.is_(False),
            )
            .group_by(Sale.customer_id)
            .subquery()
        )

        debts_subquery = (
            select(
                CustomerDebt.customer_id.label("customer_id"),
                func.coalesce(
                    func.sum(CustomerDebt.original_amount),
                    0,
                ).label("total_credit_amount"),
                func.coalesce(
                    func.sum(CustomerDebt.paid_amount),
                    0,
                ).label("total_debt_paid_amount"),
                func.coalesce(
                    func.sum(CustomerDebt.pending_amount),
                    0,
                ).label("pending_debt_amount"),
            )
            .where(CustomerDebt.is_deleted.is_(False))
            .group_by(CustomerDebt.customer_id)
            .subquery()
        )

        statement = (
            select(
                Customer.id.label("customer_id"),
                Customer.full_name,
                Customer.document_number,
                Customer.phone,
                Customer.whatsapp,
                Customer.email,
                Customer.address,
                func.coalesce(
                    sales_subquery.c.purchases_count,
                    0,
                ).label("purchases_count"),
                func.coalesce(
                    sales_subquery.c.total_purchased_amount,
                    0,
                ).label("total_purchased_amount"),
                func.coalesce(
                    sales_subquery.c.total_profit_generated,
                    0,
                ).label("total_profit_generated"),
                func.coalesce(
                    debts_subquery.c.total_credit_amount,
                    0,
                ).label("total_credit_amount"),
                func.coalesce(
                    debts_subquery.c.total_debt_paid_amount,
                    0,
                ).label("total_debt_paid_amount"),
                func.coalesce(
                    debts_subquery.c.pending_debt_amount,
                    0,
                ).label("pending_debt_amount"),
                sales_subquery.c.last_purchase_date,
                Customer.is_active,
            )
            .outerjoin(
                sales_subquery,
                sales_subquery.c.customer_id == Customer.id,
            )
            .outerjoin(
                debts_subquery,
                debts_subquery.c.customer_id == Customer.id,
            )
            .where(Customer.is_deleted.is_(False))
            .order_by(Customer.full_name.asc())
        )

        return list(db.execute(statement).mappings().all())

    @staticmethod
    def get_debts_report(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list:
        start_datetime, end_datetime = ReportRepository._date_range(
            start_date,
            end_date,
        )

        payment_subquery = (
            select(
                CustomerDebtPayment.customer_debt_id.label(
                    "customer_debt_id"
                ),
                func.count(CustomerDebtPayment.id).label(
                    "payments_count"
                ),
                func.max(CustomerDebtPayment.created_at).label(
                    "last_payment_date"
                ),
            )
            .where(CustomerDebtPayment.is_deleted.is_(False))
            .group_by(CustomerDebtPayment.customer_debt_id)
            .subquery()
        )

        statement = (
            select(
                CustomerDebt.id.label("debt_id"),
                CustomerDebt.sale_id,
                CustomerDebt.customer_id,
                Customer.full_name.label("customer_name"),
                CustomerDebt.original_amount.label(
                    "original_amount"
                ),
                CustomerDebt.paid_amount,
                CustomerDebt.pending_amount,
                CustomerDebt.status,
                CustomerDebt.created_at,
                CustomerDebt.updated_at,
                func.coalesce(
                    payment_subquery.c.payments_count,
                    0,
                ).label("payments_count"),
                payment_subquery.c.last_payment_date,
            )
            .join(
                Customer,
                Customer.id == CustomerDebt.customer_id,
            )
            .outerjoin(
                payment_subquery,
                payment_subquery.c.customer_debt_id
                == CustomerDebt.id,
            )
            .where(CustomerDebt.is_deleted.is_(False))
        )

        if start_datetime is not None:
            statement = statement.where(
                CustomerDebt.created_at >= start_datetime
            )

        if end_datetime is not None:
            statement = statement.where(
                CustomerDebt.created_at < end_datetime
            )

        statement = statement.order_by(
            CustomerDebt.created_at.desc()
        )

        return list(db.execute(statement).mappings().all())

    @staticmethod
    def get_products_report(
        db: Session,
    ) -> list:
        sales_subquery = (
            select(
                SaleItem.product_id.label("product_id"),
                func.coalesce(
                    func.sum(SaleItem.quantity),
                    0,
                ).label("sold_quantity"),
                func.coalesce(
                    func.sum(SaleItem.subtotal),
                    0,
                ).label("sales_amount"),
                func.coalesce(
                    func.sum(
                        SaleItem.subtotal - SaleItem.cost_total
                    ),
                    0,
                ).label("generated_profit"),
            )
            .join(
                Sale,
                Sale.id == SaleItem.sale_id,
            )
            .where(
                Sale.is_confirmed.is_(True),
                Sale.is_deleted.is_(False),
            )
            .group_by(SaleItem.product_id)
            .subquery()
        )

        statement = (
            select(
                Product.id.label("product_id"),
                Product.internal_code,
                Product.barcode,
                Product.name,
                Product.brand,
                ProductCategory.name.label("category_name"),
                Supplier.name.label("supplier_name"),
                Product.cost_price,
                Product.sale_price,
                Product.profit_margin,
                Product.profit_amount,
                Product.stock,
                Product.minimum_stock,
                func.coalesce(
                    sales_subquery.c.sold_quantity,
                    0,
                ).label("sold_quantity"),
                func.coalesce(
                    sales_subquery.c.sales_amount,
                    0,
                ).label("sales_amount"),
                func.coalesce(
                    sales_subquery.c.generated_profit,
                    0,
                ).label("generated_profit"),
                Product.expiration_date,
                Product.is_weighted,
                Product.is_frozen,
                Product.status,
                Product.is_active,
            )
            .outerjoin(
                ProductCategory,
                ProductCategory.id == Product.category_id,
            )
            .outerjoin(
                Supplier,
                Supplier.id == Product.supplier_id,
            )
            .outerjoin(
                sales_subquery,
                sales_subquery.c.product_id == Product.id,
            )
            .where(Product.is_deleted.is_(False))
            .order_by(Product.name.asc())
        )

        return list(db.execute(statement).mappings().all())

    @staticmethod
    def get_suppliers_report(
        db: Session,
    ) -> list:
        products_subquery = (
            select(
                Product.supplier_id.label("supplier_id"),
                func.count(Product.id).label("products_count"),
            )
            .where(
                Product.supplier_id.is_not(None),
                Product.is_deleted.is_(False),
            )
            .group_by(Product.supplier_id)
            .subquery()
        )

        purchases_subquery = (
            select(
                Purchase.supplier_id.label("supplier_id"),
                func.count(Purchase.id).label("purchases_count"),
                func.coalesce(
                    func.sum(Purchase.total_amount),
                    0,
                ).label("total_purchased_amount"),
                func.max(Purchase.purchase_date).label(
                    "last_purchase_date"
                ),
            )
            .where(
                Purchase.supplier_id.is_not(None),
                Purchase.is_confirmed.is_(True),
                Purchase.is_deleted.is_(False),
            )
            .group_by(Purchase.supplier_id)
            .subquery()
        )

        statement = (
            select(
                Supplier.id.label("supplier_id"),
                Supplier.name,
                Supplier.ruc,
                Supplier.phone,
                Supplier.whatsapp,
                Supplier.email,
                Supplier.contact_name,
                func.coalesce(
                    products_subquery.c.products_count,
                    0,
                ).label("products_count"),
                func.coalesce(
                    purchases_subquery.c.purchases_count,
                    0,
                ).label("purchases_count"),
                func.coalesce(
                    purchases_subquery.c.total_purchased_amount,
                    0,
                ).label("total_purchased_amount"),
                purchases_subquery.c.last_purchase_date,
                Supplier.is_active,
            )
            .outerjoin(
                products_subquery,
                products_subquery.c.supplier_id == Supplier.id,
            )
            .outerjoin(
                purchases_subquery,
                purchases_subquery.c.supplier_id == Supplier.id,
            )
            .where(Supplier.is_deleted.is_(False))
            .order_by(Supplier.name.asc())
        )

        return list(db.execute(statement).mappings().all())