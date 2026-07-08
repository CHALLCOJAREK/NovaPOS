from sqlalchemy.orm import Session

from app.models.sale import Sale


class SaleRepository:

    def get_all(
        self,
        db: Session
    ) -> list[Sale]:

        return (
            db.query(Sale)
            .filter(
                Sale.is_deleted == False
            )
            .all()
        )


    def get_by_id(
        self,
        db: Session,
        sale_id: int
    ) -> Sale | None:

        return (
            db.query(Sale)
            .filter(
                Sale.id == sale_id,
                Sale.is_deleted == False
            )
            .first()
        )


    def create(
        self,
        db: Session,
        sale: Sale
    ) -> Sale:

        db.add(sale)
        db.commit()
        db.refresh(sale)

        return sale


    def soft_delete(
        self,
        db: Session,
        sale: Sale
    ) -> Sale:

        sale.is_deleted = True

        db.commit()
        db.refresh(sale)

        return sale