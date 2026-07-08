from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.role_repository import RoleRepository
from app.schemas.role import RoleCreate, RoleUpdate
from app.models.role import Role


class RoleService:
    def __init__(self, db: Session):
        self.db = db
        self.role_repository = RoleRepository(db)

    def get_roles(self) -> list[Role]:
        return self.role_repository.get_all()

    def get_role_by_id(self, role_id: int) -> Role:
        role = self.role_repository.get_by_id(role_id)

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol no encontrado."
            )

        return role

    def create_role(self, role_data: RoleCreate) -> Role:
        existing_role = self.role_repository.get_by_name(role_data.name)

        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un rol con este nombre."
            )

        return self.role_repository.create(role_data)

    def update_role(self, role_id: int, role_data: RoleUpdate) -> Role:
        role = self.role_repository.get_by_id(role_id)

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol no encontrado."
            )

        if role_data.name:
            existing_role = self.role_repository.get_by_name(role_data.name)

            if existing_role and existing_role.id != role_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe otro rol con este nombre."
                )

        return self.role_repository.update(role, role_data)

    def delete_role(self, role_id: int) -> Role:
        role = self.role_repository.get_by_id(role_id)

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol no encontrado."
            )

        return self.role_repository.soft_delete(role)