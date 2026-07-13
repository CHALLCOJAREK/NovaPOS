from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.inventory_movement import InventoryMovement
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.repositories.sale_repository import SaleRepository
from app.schemas.customer_debt import CustomerDebtCreate
from app.schemas.sale import SaleCreate
from app.services.cash_service import CashService
from app.services.customer_debt_service import CustomerDebtService
from app.services.sale_document_service import SaleDocumentService


class SaleService:

    def __init__(self):
        self.repository = SaleRepository()

    def create_sale(
        self,
        db: Session,
        data: SaleCreate,
    ) -> Sale:

        if (
            data.payment_method == "CREDIT"
            and not data.customer_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Cliente requerido para venta fiada",
            )

        subtotal = Decimal("0.00")
        total_cost = Decimal("0.00")

        sale_items = []

        for item in data.items:

            product = (
                db.query(Product)
                .filter(
                    Product.id == item.product_id,
                    Product.is_deleted == False,
                    Product.is_active == True,
                )
                .first()
            )

            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Producto {item.product_id} "
                        "no disponible"
                    ),
                )

            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Stock insuficiente para "
                        f"{product.name}"
                    ),
                )

            item_subtotal = (
                product.sale_price
                * item.quantity
            )

            item_cost = (
                product.cost_price
                * item.quantity
            )

            item_profit = (
                item_subtotal
                - item_cost
            )

            subtotal += item_subtotal
            total_cost += item_cost

            sale_item = SaleItem(
                product_id=product.id,
                quantity=item.quantity,
                unit_price=product.sale_price,
                unit_cost=product.cost_price,
                subtotal=item_subtotal,
                cost_total=item_cost,
                profit_amount=item_profit,
            )

            sale_items.append(sale_item)

        total_amount = (
            subtotal
            - data.discount_amount
        )

        if total_amount < Decimal("0.00"):
            raise HTTPException(
                status_code=400,
                detail=(
                    "El descuento no puede superar "
                    "el subtotal de la venta"
                ),
            )

        profit_amount = (
            total_amount
            - total_cost
        )

        sale = Sale(
            customer_id=data.customer_id,
            document_type=data.document_type,
            payment_method=data.payment_method,
            subtotal=subtotal,
            discount_amount=data.discount_amount,
            total_amount=total_amount,
            total_cost=total_cost,
            profit_amount=profit_amount,
            notes=data.notes,
            is_confirmed=True,
        )

        sale.items = sale_items

        try:
            db.add(sale)
            db.flush()

            for item in sale_items:

                product = (
                    db.query(Product)
                    .filter(
                        Product.id == item.product_id
                    )
                    .first()
                )

                if product is None:
                    raise HTTPException(
                        status_code=404,
                        detail=(
                            f"Producto {item.product_id} "
                            "no encontrado al actualizar inventario"
                        ),
                    )

                previous_stock = product.stock

                product.stock -= item.quantity

                movement = InventoryMovement(
                    product_id=product.id,
                    movement_type="OUT",
                    quantity=item.quantity,
                    reason="Venta realizada",
                    reference_type="SALE",
                    reference_id=sale.id,
                    previous_stock=previous_stock,
                    new_stock=product.stock,
                )

                db.add(movement)

            CashService(db).register_sale_payment(
                sale_id=sale.id,
                payment_method=sale.payment_method,
                total_amount=sale.total_amount,
                profit_amount=sale.profit_amount,
            )

            if sale.payment_method == "CREDIT":

                debt_data = CustomerDebtCreate(
                    customer_id=sale.customer_id,
                    sale_id=sale.id,
                    original_amount=sale.total_amount,
                )

                CustomerDebtService.create_debt(
                    db,
                    debt_data,
                )

            db.commit()
            db.refresh(sale)

        except HTTPException:
            db.rollback()
            raise

        except Exception as exc:
            db.rollback()

            raise HTTPException(
                status_code=500,
                detail=(
                    "No se pudo registrar completamente "
                    "la venta"
                ),
            ) from exc

        SaleDocumentService.create_for_sale(
            db=db,
            sale=sale,
        )

        db.refresh(sale)

        return sale