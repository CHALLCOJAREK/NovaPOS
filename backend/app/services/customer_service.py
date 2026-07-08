from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    def __init__(self) -> None:
        self.customer_repository = CustomerRepository()

    def get_all_customers(self, db: Session):
        return self.customer_repository.get_all(db)

    def get_customer_by_id(self, db: Session, customer_id: int):
        customer = self.customer_repository.get_by_id(db, customer_id)

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )

        return customer

    def create_customer(self, db: Session, customer_data: CustomerCreate):
        self._validate_unique_fields(db, customer_data)

        return self.customer_repository.create(db, customer_data)

    def update_customer(
        self,
        db: Session,
        customer_id: int,
        customer_data: CustomerUpdate,
    ):
        customer = self.get_customer_by_id(db, customer_id)

        self._validate_unique_fields(
            db=db,
            customer_data=customer_data,
            current_customer_id=customer_id,
        )

        return self.customer_repository.update(db, customer, customer_data)

    def delete_customer(self, db: Session, customer_id: int):
        customer = self.get_customer_by_id(db, customer_id)

        return self.customer_repository.soft_delete(db, customer)

    def _validate_unique_fields(
        self,
        db: Session,
        customer_data: CustomerCreate | CustomerUpdate,
        current_customer_id: int | None = None,
    ) -> None:
        data = customer_data.model_dump(exclude_unset=True)

        document_number = data.get("document_number")
        phone = data.get("phone")
        whatsapp = data.get("whatsapp")
        email = data.get("email")

        if document_number:
            existing_customer = self.customer_repository.get_by_document_number(
                db,
                document_number,
            )
            self._raise_if_duplicate(
                existing_customer,
                current_customer_id,
                "Ya existe un cliente con este documento",
            )

        if phone:
            existing_customer = self.customer_repository.get_by_phone(
                db,
                phone,
            )
            self._raise_if_duplicate(
                existing_customer,
                current_customer_id,
                "Ya existe un cliente con este teléfono",
            )

        if whatsapp:
            existing_customer = self.customer_repository.get_by_whatsapp(
                db,
                whatsapp,
            )
            self._raise_if_duplicate(
                existing_customer,
                current_customer_id,
                "Ya existe un cliente con este WhatsApp",
            )

        if email:
            existing_customer = self.customer_repository.get_by_email(
                db,
                email,
            )
            self._raise_if_duplicate(
                existing_customer,
                current_customer_id,
                "Ya existe un cliente con este correo",
            )

    def _raise_if_duplicate(
        self,
        existing_customer,
        current_customer_id: int | None,
        message: str,
    ) -> None:
        if existing_customer and existing_customer.id != current_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )