from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.permission_repository import PermissionRepository
from app.schemas.permission import PermissionCreate, PermissionUpdate
from app.models.permission import Permission


class PermissionService:
    def __init__(self, db: Session):
        self.db = db
        self.permission_repository = PermissionRepository(db)

    def get_permissions(self) -> list[Permission]:
        return self.permission_repository.get_all()

    def get_permission_by_id(self, permission_id: int) -> Permission:
        permission = self.permission_repository.get_by_id(permission_id)

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permiso no encontrado."
            )

        return permission

    def create_permission(self, permission_data: PermissionCreate) -> Permission:
        existing_permission = self.permission_repository.get_by_code(
            permission_data.code
        )

        if existing_permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un permiso con este código."
            )

        return self.permission_repository.create(permission_data)

    def update_permission(
        self,
        permission_id: int,
        permission_data: PermissionUpdate
    ) -> Permission:
        permission = self.permission_repository.get_by_id(permission_id)

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permiso no encontrado."
            )

        if permission_data.code:
            existing_permission = self.permission_repository.get_by_code(
                permission_data.code
            )

            if existing_permission and existing_permission.id != permission_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe otro permiso con este código."
                )

        return self.permission_repository.update(permission, permission_data)

    def delete_permission(self, permission_id: int) -> Permission:
        permission = self.permission_repository.get_by_id(permission_id)

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permiso no encontrado."
            )

        return self.permission_repository.soft_delete(permission)