from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.orm import Session

from app.models.cash_register import CashRegister
from app.models.customer import Customer
from app.models.customer_debt import CustomerDebt
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.supplier import Supplier
from app.models.sale_document import SaleDocument


class DashboardRepository:
    """
    Repository de consultas comerciales para el Dashboard de NovaPOS.

    Esta clase únicamente accede a SQLAlchemy.
    No contiene reglas de presentación ni construye schemas Pydantic.
    """

    @staticmethod
    def _get_day_range(target_date: date) -> tuple[datetime, datetime]:
        start_datetime = datetime.combine(target_date, time.min)
        end_datetime = start_datetime + timedelta(days=1)

        return start_datetime, end_datetime

    @staticmethod
    def get_daily_sales_summary(
        db: Session,
        target_date: date,
    ) -> dict[str, Decimal]:
        start_datetime, end_datetime = DashboardRepository._get_day_range(
            target_date
        )

        statement = select(
            func.coalesce(func.sum(Sale.total_amount), 0).label(
                "sales_amount"
            ),
            func.coalesce(func.sum(Sale.profit_amount), 0).label(
                "profit_amount"
            ),
        ).where(
            Sale.created_at >= start_datetime,
            Sale.created_at < end_datetime,
            Sale.is_confirmed.is_(True),
            Sale.is_deleted.is_(False),
        )

        result = db.execute(statement).one()

        return {
            "sales_amount": Decimal(str(result.sales_amount or 0)),
            "profit_amount": Decimal(str(result.profit_amount or 0)),
        }

    @staticmethod
    def get_daily_sales_by_payment_method(
        db: Session,
        target_date: date,
    ) -> dict[str, Decimal]:
        start_datetime, end_datetime = DashboardRepository._get_day_range(
            target_date
        )

        statement = (
            select(
                Sale.payment_method,
                func.coalesce(func.sum(Sale.total_amount), 0).label(
                    "total_amount"
                ),
            )
            .where(
                Sale.created_at >= start_datetime,
                Sale.created_at < end_datetime,
                Sale.is_confirmed.is_(True),
                Sale.is_deleted.is_(False),
            )
            .group_by(Sale.payment_method)
        )

        rows = db.execute(statement).all()

        totals = {
            "CASH": Decimal("0.00"),
            "YAPE": Decimal("0.00"),
            "CREDIT": Decimal("0.00"),
        }

        for payment_method, total_amount in rows:
            method = str(payment_method).upper()

            if method in totals:
                totals[method] = Decimal(str(total_amount or 0))

        return totals

    @staticmethod
    def get_daily_purchases_amount(
        db: Session,
        target_date: date,
    ) -> Decimal:
        statement = select(
            func.coalesce(func.sum(Purchase.total_amount), 0)
        ).where(
            Purchase.purchase_date == target_date,
            Purchase.is_confirmed.is_(True),
            Purchase.is_deleted.is_(False),
        )

        result = db.execute(statement).scalar_one()

        return Decimal(str(result or 0))

    @staticmethod
    def get_current_cash_register(
        db: Session,
    ) -> CashRegister | None:
        statement = (
            select(CashRegister)
            .where(
                CashRegister.closed_at.is_(None),
                CashRegister.is_deleted.is_(False),
            )
            .order_by(CashRegister.opened_at.desc())
            .limit(1)
        )

        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def get_daily_products_sold_quantity(
        db: Session,
        target_date: date,
    ) -> Decimal:
        start_datetime, end_datetime = DashboardRepository._get_day_range(
            target_date
        )

        statement = (
            select(
                func.coalesce(func.sum(SaleItem.quantity), 0)
            )
            .join(
                Sale,
                Sale.id == SaleItem.sale_id,
            )
            .where(
                Sale.created_at >= start_datetime,
                Sale.created_at < end_datetime,
                Sale.is_confirmed.is_(True),
                Sale.is_deleted.is_(False),
            )
        )

        result = db.execute(statement).scalar_one()

        return Decimal(str(result or 0))

    @staticmethod
    def count_low_stock_products(
        db: Session,
    ) -> int:
        statement = select(func.count(Product.id)).where(
            Product.is_active.is_(True),
            Product.is_deleted.is_(False),
            Product.stock <= Product.minimum_stock,
        )

        return int(db.execute(statement).scalar_one() or 0)

    @staticmethod
    def count_expiring_products(
        db: Session,
        start_date: date,
        end_date: date,
    ) -> int:
        statement = select(func.count(Product.id)).where(
            Product.is_active.is_(True),
            Product.is_deleted.is_(False),
            Product.stock > 0,
            Product.expiration_date.is_not(None),
            Product.expiration_date >= start_date,
            Product.expiration_date <= end_date,
        )

        return int(db.execute(statement).scalar_one() or 0)

    @staticmethod
    def count_purchase_suggestions(
        db: Session,
    ) -> int:
        statement = select(func.count(Product.id)).where(
            Product.is_active.is_(True),
            Product.is_deleted.is_(False),
            Product.stock <= Product.minimum_stock,
        )

        return int(db.execute(statement).scalar_one() or 0)

    @staticmethod
    def count_customers_with_debt(
        db: Session,
    ) -> int:
        statement = select(
            func.count(func.distinct(CustomerDebt.customer_id))
        ).where(
            CustomerDebt.pending_amount > 0,
            CustomerDebt.is_deleted.is_(False),
        )

        return int(db.execute(statement).scalar_one() or 0)

    @staticmethod
    def get_total_pending_debt_amount(
        db: Session,
    ) -> Decimal:
        statement = select(
            func.coalesce(func.sum(CustomerDebt.pending_amount), 0)
        ).where(
            CustomerDebt.pending_amount > 0,
            CustomerDebt.is_deleted.is_(False),
        )

        result = db.execute(statement).scalar_one()

        return Decimal(str(result or 0))

    @staticmethod
    def count_customers(
        db: Session,
    ) -> int:
        statement = select(func.count(Customer.id)).where(
            Customer.is_active.is_(True),
            Customer.is_deleted.is_(False),
        )

        return int(db.execute(statement).scalar_one() or 0)

    @staticmethod
    def count_suppliers(
        db: Session,
    ) -> int:
        statement = select(func.count(Supplier.id)).where(
            Supplier.is_active.is_(True),
            Supplier.is_deleted.is_(False),
        )

        return int(db.execute(statement).scalar_one() or 0)

    @staticmethod
    def count_active_products(
        db: Session,
    ) -> int:
        statement = select(func.count(Product.id)).where(
            Product.is_active.is_(True),
            Product.is_deleted.is_(False),
        )

        return int(db.execute(statement).scalar_one() or 0)

    @staticmethod
    def get_top_products(
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 10,
    ) -> list:
        statement: Select = (
            select(
                Product.id.label("product_id"),
                Product.internal_code,
                Product.barcode,
                Product.name,
                Product.brand,
                func.coalesce(
                    func.sum(SaleItem.quantity),
                    0,
                ).label("quantity_sold"),
                func.coalesce(
                    func.sum(SaleItem.subtotal),
                    0,
                ).label("sales_amount"),
                func.coalesce(
                    func.sum(
                        SaleItem.subtotal - SaleItem.cost_total
                    ),
                    0,
                ).label("profit_amount"),
            )
            .join(
                SaleItem,
                SaleItem.product_id == Product.id,
            )
            .join(
                Sale,
                Sale.id == SaleItem.sale_id,
            )
            .where(
                Product.is_deleted.is_(False),
                Sale.is_confirmed.is_(True),
                Sale.is_deleted.is_(False),
            )
        )

        if start_date is not None:
            start_datetime = datetime.combine(start_date, time.min)
            statement = statement.where(
                Sale.created_at >= start_datetime
            )

        if end_date is not None:
            end_datetime = datetime.combine(
                end_date + timedelta(days=1),
                time.min,
            )
            statement = statement.where(
                Sale.created_at < end_datetime
            )

        statement = (
            statement
            .group_by(
                Product.id,
                Product.internal_code,
                Product.barcode,
                Product.name,
                Product.brand,
            )
            .order_by(
                func.sum(SaleItem.quantity).desc(),
                func.sum(SaleItem.subtotal).desc(),
            )
            .limit(limit)
        )

        return list(db.execute(statement).mappings().all())

    @staticmethod
    def get_recent_sales(
        db: Session,
        limit: int = 10,
    ) -> list:
        statement = (
            select(
                Sale.id.label("sale_id"),
                Sale.customer_id,
                Customer.full_name.label("customer_name"),
                Sale.document_type,
                SaleDocument.full_number.label("document_number"),
                Sale.payment_method,
                Sale.total_amount,
                Sale.profit_amount,
                Sale.created_at,
            )
            .outerjoin(
                Customer,
                Customer.id == Sale.customer_id,
            )
            .outerjoin(
                SaleDocument,
                (
                    (SaleDocument.sale_id == Sale.id)
                    & (SaleDocument.is_deleted.is_(False))
                ),
            )
            .where(
                Sale.is_confirmed.is_(True),
                Sale.is_deleted.is_(False),
            )
            .order_by(Sale.created_at.desc())
            .limit(limit)
        )

        return list(db.execute(statement).mappings().all())

    @staticmethod
    def count_confirmed_sales(
        db: Session,
    ) -> int:
        statement = select(func.count(Sale.id)).where(
            Sale.is_confirmed.is_(True),
            Sale.is_deleted.is_(False),
        )

        return int(db.execute(statement).scalar_one() or 0)

    @staticmethod
    def get_stock_alerts(
        db: Session,
        limit: int = 100,
    ) -> list:
        missing_stock_expression = (
            Product.minimum_stock - Product.stock
        )

        statement = (
            select(
                Product.id.label("product_id"),
                Product.internal_code,
                Product.barcode,
                Product.name,
                Product.brand,
                Product.stock.label("current_stock"),
                Product.minimum_stock,
                missing_stock_expression.label("missing_stock"),
                Product.status,
            )
            .where(
                Product.is_active.is_(True),
                Product.is_deleted.is_(False),
                Product.stock <= Product.minimum_stock,
            )
            .order_by(
                Product.stock.asc(),
                Product.name.asc(),
            )
            .limit(limit)
        )

        return list(db.execute(statement).mappings().all())

    @staticmethod
    def get_expiring_products(
        db: Session,
        start_date: date,
        end_date: date,
        limit: int = 100,
    ) -> list:
        statement = (
            select(
                Product.id.label("product_id"),
                Product.internal_code,
                Product.barcode,
                Product.name,
                Product.brand,
                Product.stock,
                Product.expiration_date,
                Product.batch,
            )
            .where(
                Product.is_active.is_(True),
                Product.is_deleted.is_(False),
                Product.stock > 0,
                Product.expiration_date.is_not(None),
                Product.expiration_date >= start_date,
                Product.expiration_date <= end_date,
            )
            .order_by(
                Product.expiration_date.asc(),
                Product.name.asc(),
            )
            .limit(limit)
        )

        return list(db.execute(statement).mappings().all())

    @staticmethod
    def get_purchase_suggestions(
        db: Session,
        limit: int = 100,
    ) -> list:
        suggested_quantity_expression = (
            Product.minimum_stock - Product.stock
        )

        statement = (
            select(
                Product.id.label("product_id"),
                Product.internal_code,
                Product.barcode,
                Product.name,
                Product.brand,
                Product.stock.label("current_stock"),
                Product.minimum_stock,
                suggested_quantity_expression.label(
                    "suggested_quantity"
                ),
                Product.supplier_id,
                Supplier.name.label("supplier_name"),
            )
            .outerjoin(
                Supplier,
                Supplier.id == Product.supplier_id,
            )
            .where(
                Product.is_active.is_(True),
                Product.is_deleted.is_(False),
                Product.stock <= Product.minimum_stock,
            )
            .order_by(
                Product.stock.asc(),
                Product.name.asc(),
            )
            .limit(limit)
        )

        return list(db.execute(statement).mappings().all())

    @staticmethod
    def get_customer_debts(
        db: Session,
        limit: int = 100,
    ) -> list:
        statement = (
            select(
                Customer.id.label("customer_id"),
                Customer.full_name.label("customer_name"),
                Customer.document_number,
                Customer.phone,
                Customer.whatsapp,
                func.coalesce(
                    func.sum(CustomerDebt.original_amount),
                    0,
                ).label("total_debt_amount"),
                func.coalesce(
                    func.sum(CustomerDebt.paid_amount),
                    0,
                ).label("total_paid_amount"),
                func.coalesce(
                    func.sum(CustomerDebt.pending_amount),
                    0,
                ).label("pending_amount"),
                func.count(CustomerDebt.id).label(
                    "pending_debts_count"
                ),
                func.min(CustomerDebt.created_at).label(
                    "oldest_debt_date"
                ),
            )
            .join(
                CustomerDebt,
                CustomerDebt.customer_id == Customer.id,
            )
            .where(
                Customer.is_deleted.is_(False),
                CustomerDebt.pending_amount > 0,
                CustomerDebt.is_deleted.is_(False),
            )
            .group_by(
                Customer.id,
                Customer.full_name,
                Customer.document_number,
                Customer.phone,
                Customer.whatsapp,
            )
            .order_by(
                func.sum(CustomerDebt.pending_amount).desc()
            )
            .limit(limit)
        )

        return list(db.execute(statement).mappings().all())