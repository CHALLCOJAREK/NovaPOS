from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository

from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User

from app.core.security import hash_password


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)

    def get_users(self) -> list[User]:
        return self.user_repository.get_all()

    def get_user_by_id(self, user_id: int) -> User:
        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado."
            )

        return user

    def create_user(
        self,
        user_data: UserCreate
    ) -> User:

        existing_username = (
            self.user_repository.get_by_username(
                user_data.username
            )
        )

        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya existe."
            )

        existing_email = (
            self.user_repository.get_by_email(
                user_data.email
            )
        )

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya está registrado."
            )

        role = self.role_repository.get_by_id(
            user_data.role_id
        )

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol asignado no existe."
            )

        hashed_password = hash_password(
            user_data.password
            )

        return self.user_repository.create(
                user_data,
                hashed_password
            )

    def update_user(
        self,
        user_id: int,
        user_data: UserUpdate
    ) -> User:

        user = self.user_repository.get_by_id(
            user_id
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado."
            )

        if user_data.email:

            existing_email = (
                self.user_repository.get_by_email(
                    user_data.email
                )
            )

            if (
                existing_email
                and existing_email.id != user_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El correo pertenece a otro usuario."
                )

        if user_data.role_id:

            role = self.role_repository.get_by_id(
                user_data.role_id
            )

            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Rol asignado no existe."
                )

        return self.user_repository.update(
            user,
            user_data
        )

    def delete_user(
        self,
        user_id: int
    ) -> User:

        user = self.user_repository.get_by_id(
            user_id
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado."
            )

        return self.user_repository.soft_delete(
            user
        )