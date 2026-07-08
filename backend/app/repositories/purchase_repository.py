from sqlalchemy.orm import Session, joinedload

from app.models.purchase import Purchase
from app.models.purchase_item import PurchaseItem


class PurchaseRepository:

    def __init__(self, db: Session):
        self.db = db


    def get_all(self):
        return (
            self.db.query(Purchase)
            .options(joinedload(Purchase.items))
            .filter(Purchase.is_deleted == False)
            .all()
        )


    def get_by_id(self, purchase_id: int):
        return (
            self.db.query(Purchase)
            .options(joinedload(Purchase.items))
            .filter(
                Purchase.id == purchase_id,
                Purchase.is_deleted == False,
            )
            .first()
        )


    def create(self, purchase: Purchase):
        self.db.add(purchase)
        self.db.flush()
        return purchase


    def create_item(self, item: PurchaseItem):
        self.db.add(item)
        return item


    def soft_delete(self, purchase: Purchase):
        purchase.is_deleted = True
        self.db.commit()
        self.db.refresh(purchase)

        return purchase


    def commit(self):
        self.db.commit()


    def refresh(self, entity):
        self.db.refresh(entity)
        return entity