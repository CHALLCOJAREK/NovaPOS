from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerRepository:
    def get_all(self, db: Session) -> list[Customer]:
        return (
            db.query(Customer)
            .filter(Customer.is_deleted == False)
            .order_by(Customer.id.desc())
            .all()
        )

    def get_by_id(self, db: Session, customer_id: int) -> Customer | None:
        return (
            db.query(Customer)
            .filter(
                Customer.id == customer_id,
                Customer.is_deleted == False,
            )
            .first()
        )

    def get_by_document_number(self, db: Session, document_number: str) -> Customer | None:
        return (
            db.query(Customer)
            .filter(
                Customer.document_number == document_number,
                Customer.is_deleted == False,
            )
            .first()
        )

    def get_by_phone(self, db: Session, phone: str) -> Customer | None:
        return (
            db.query(Customer)
            .filter(
                Customer.phone == phone,
                Customer.is_deleted == False,
            )
            .first()
        )

    def get_by_whatsapp(self, db: Session, whatsapp: str) -> Customer | None:
        return (
            db.query(Customer)
            .filter(
                Customer.whatsapp == whatsapp,
                Customer.is_deleted == False,
            )
            .first()
        )

    def get_by_email(self, db: Session, email: str) -> Customer | None:
        return (
            db.query(Customer)
            .filter(
                Customer.email == email,
                Customer.is_deleted == False,
            )
            .first()
        )

    def create(self, db: Session, customer_data: CustomerCreate) -> Customer:
        customer = Customer(**customer_data.model_dump())

        db.add(customer)
        db.commit()
        db.refresh(customer)

        return customer

    def update(
        self,
        db: Session,
        customer: Customer,
        customer_data: CustomerUpdate,
    ) -> Customer:
        update_data = customer_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(customer, field, value)

        db.commit()
        db.refresh(customer)

        return customer

    def soft_delete(self, db: Session, customer: Customer) -> Customer:
        customer.is_active = False
        customer.is_deleted = True

        db.commit()
        db.refresh(customer)

        return customer