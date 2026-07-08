from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.purchase import Purchase
from app.models.purchase_item import PurchaseItem
from app.models.inventory_movement import InventoryMovement

from app.repositories.purchase_repository import PurchaseRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.supplier_repository import SupplierRepository

from app.schemas.purchase import PurchaseCreate


class PurchaseService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = PurchaseRepository(db)
        self.product_repository = ProductRepository(db)
        self.supplier_repository = SupplierRepository()


    def get_all(self):
        return self.repository.get_all()


    def get_by_id(self, purchase_id: int):
        purchase = self.repository.get_by_id(purchase_id)

        if not purchase:
            raise HTTPException(
                status_code=404,
                detail="Compra no encontrada",
            )

        return purchase


    def create(self, data: PurchaseCreate):

        supplier = self.supplier_repository.get_by_id(
            self.db,
            data.supplier_id
        )

        if not supplier:
            raise HTTPException(
                status_code=400,
                detail="Proveedor no encontrado o eliminado",
            )


        subtotal = Decimal("0.00")

        purchase = Purchase(
            supplier_id=data.supplier_id,
            document_type=data.document_type,
            document_number=data.document_number,
            purchase_date=data.purchase_date,
            subtotal=0,
            tax_amount=0,
            total_amount=0,
            notes=data.notes,
            ocr_source_path=data.ocr_source_path,
        )

        self.repository.create(purchase)


        for item in data.items:

            product = self.product_repository.get_by_id(
                item.product_id
            )

            if not product:
                raise HTTPException(
                    status_code=400,
                    detail=f"Producto {item.product_id} no encontrado o eliminado",
                )


            unit_cost = (
                item.package_total_cost /
                item.unit_quantity
            )

            previous_stock = product.stock
            previous_cost = product.cost_price

            new_stock = (
                product.stock +
                item.unit_quantity
            )


            purchase_item = PurchaseItem(
                purchase_id=purchase.id,
                product_id=item.product_id,

                package_total_cost=item.package_total_cost,
                unit_quantity=item.unit_quantity,

                unit_cost=unit_cost,

                previous_cost=previous_cost,
                new_cost=unit_cost,

                previous_stock=previous_stock,
                new_stock=new_stock,

                expiration_date=item.expiration_date,
                batch=item.batch,
                notes=item.notes,
            )

            self.repository.create_item(
                purchase_item
            )


            product.cost_price = unit_cost
            product.stock = new_stock
            product.profit_amount = product.sale_price - unit_cost

            if unit_cost > 0:
                    product.profit_margin = (product.profit_amount / unit_cost) * 100
            else:
                    product.profit_margin = 0

            movement = InventoryMovement(
                product_id=product.id,
                movement_type="IN",

                quantity=item.unit_quantity,

                previous_stock=previous_stock,
                new_stock=new_stock,

                reason="Compra de mercadería",

                reference_type="PURCHASE",
                reference_id=purchase.id,

                notes=f"Compra documento {data.document_number}",
            )

            self.db.add(movement)

            subtotal += item.package_total_cost


        purchase.subtotal = subtotal
        purchase.total_amount = subtotal
        purchase.tax_amount = 0


        self.repository.commit()

        self.repository.refresh(
            purchase
        )

        return purchase


    def delete(self, purchase_id: int):

        purchase = self.get_by_id(
            purchase_id
        )

        return self.repository.soft_delete(
            purchase
        )