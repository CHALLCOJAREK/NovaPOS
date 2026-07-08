from sqlalchemy.orm import Session

from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate


class RoleRepository:
    """
    Repository for Role database operations.
    """

    def __init__(self, db: Session):
        self.db = db


    def get_by_id(
        self,
        role_id: int,
    ) -> Role | None:

        return (
            self.db
            .query(Role)
            .filter(
                Role.id == role_id,
                Role.is_deleted == False,
            )
            .first()
        )


    def get_by_name(
        self,
        name: str,
    ) -> Role | None:

        return (
            self.db
            .query(Role)
            .filter(
                Role.name == name,
                Role.is_deleted == False,
            )
            .first()
        )


    def get_all(
        self,
    ) -> list[Role]:

        return (
            self.db
            .query(Role)
            .filter(
                Role.is_deleted == False,
            )
            .all()
        )


    def create(
        self,
        role_data: RoleCreate,
    ) -> Role:

        role = Role(
            **role_data.model_dump()
        )

        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)

        return role


    def update(
        self,
        role: Role,
        role_data: RoleUpdate,
    ) -> Role:

        update_data = role_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(
                role,
                field,
                value,
            )

        self.db.commit()
        self.db.refresh(role)

        return role


    def soft_delete(
        self,
        role: Role,
    ) -> Role:

        role.is_deleted = True

        self.db.commit()
        self.db.refresh(role)

        return role