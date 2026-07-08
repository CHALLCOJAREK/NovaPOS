from datetime import datetime, timezone

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserLogin
from app.models.user import User

from app.core.security import verify_password, create_access_token


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def authenticate_user(
        self,
        login_data: UserLogin
    ) -> User:

        user = self.user_repository.get_by_username(
            login_data.username
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas."
            )

        if user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no disponible."
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo."
            )

        password_is_valid = verify_password(
            login_data.password,
            user.hashed_password
        )

        if not password_is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas."
            )

        user.last_login_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(user)

        return user

    def login(
        self,
        login_data: UserLogin
    ) -> dict:

        user = self.authenticate_user(
            login_data
        )

        access_token = create_access_token(
            subject=user.username,
            extra_data={
                "user_id": user.id,
                "role_id": user.role_id
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }