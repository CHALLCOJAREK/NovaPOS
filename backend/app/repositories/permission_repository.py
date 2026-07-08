from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate


class PermissionRepository:
    """
    Repository for Permission database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, permission_id: int) -> Permission | None:
        return (
            self.db.query(Permission)
            .filter(
                Permission.id == permission_id,
                Permission.is_deleted == False,
            )
            .first()
        )

    def get_by_code(self, code: str) -> Permission | None:
        return (
            self.db.query(Permission)
            .filter(
                Permission.code == code,
                Permission.is_deleted == False,
            )
            .first()
        )

    def get_all(self) -> list[Permission]:
        return (
            self.db.query(Permission)
            .filter(Permission.is_deleted == False)
            .all()
        )

    def create(self, permission_data: PermissionCreate) -> Permission:
        permission = Permission(
            **permission_data.model_dump()
        )

        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)

        return permission

    def update(
        self,
        permission: Permission,
        permission_data: PermissionUpdate,
    ) -> Permission:
        update_data = permission_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(permission, field, value)

        self.db.commit()
        self.db.refresh(permission)

        return permission

    def soft_delete(self, permission: Permission) -> Permission:
        permission.is_deleted = True

        self.db.commit()
        self.db.refresh(permission)

        return permission