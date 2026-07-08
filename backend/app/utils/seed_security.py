from app.db.session import SessionLocal

from app.repositories.role_repository import RoleRepository
from app.repositories.permission_repository import PermissionRepository
from app.repositories.user_repository import UserRepository

from app.schemas.role import RoleCreate
from app.schemas.permission import PermissionCreate
from app.schemas.user import UserCreate

from app.core.security import hash_password


def seed_security():

    db = SessionLocal()

    try:
        role_repository = RoleRepository(db)
        permission_repository = PermissionRepository(db)
        user_repository = UserRepository(db)

        # ==========================
        # ROLE ADMINISTRADOR
        # ==========================

        admin_role = (
            role_repository.get_by_name(
                "Administrador"
            )
        )

        if not admin_role:
            admin_role = role_repository.create(
                RoleCreate(
                    name="Administrador",
                    description="Acceso completo al sistema NovaPOS"
                )
            )

        # ==========================
        # PERMISOS BASE
        # ==========================

        permissions = [
            {
                "code": "security.full",
                "name": "Control total seguridad",
                "module": "Seguridad",
                "description": "Administrar usuarios, roles y permisos"
            }
        ]

        for item in permissions:

            exists = (
                permission_repository.get_by_code(
                    item["code"]
                )
            )

            if not exists:
                permission_repository.create(
                    PermissionCreate(
                        **item
                    )
                )

        # ==========================
        # USUARIO ADMIN
        # ==========================

        admin_user = (
            user_repository.get_by_username(
                "admin"
            )
        )

        if not admin_user:

            user = UserCreate(
                username="admin",
                email="admin@novapos.com",
                full_name="Administrador NovaPOS",
                password="Admin123*",
                role_id=admin_role.id
            )

            hashed_password = hash_password(
                user.password
            )

            user_repository.create(
                user,
                hashed_password
            )

        print(
            "Seed seguridad ejecutado correctamente."
        )

    finally:
        db.close()


if __name__ == "__main__":
    seed_security()