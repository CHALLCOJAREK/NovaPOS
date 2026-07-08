from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository:
    """
    Repository for User database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return (
            self.db.query(User)
            .filter(
                User.id == user_id,
                User.is_deleted == False,
            )
            .first()
        )

    def get_by_username(self, username: str) -> User | None:
        return (
            self.db.query(User)
            .filter(
                User.username == username,
                User.is_deleted == False,
            )
            .first()
        )

    def get_by_email(self, email: str) -> User | None:
        return (
            self.db.query(User)
            .filter(
                User.email == email,
                User.is_deleted == False,
            )
            .first()
        )

    def get_all(self) -> list[User]:
        return (
            self.db.query(User)
            .filter(User.is_deleted == False)
            .all()
        )

    def create(
        self,
        user_data: UserCreate,
        hashed_password: str,
    ) -> User:
        data = user_data.model_dump()
        data.pop("password")

        user = User(
            **data,
            hashed_password=hashed_password,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def update(
        self,
        user: User,
        user_data: UserUpdate,
        hashed_password: str | None = None,
    ) -> User:
        update_data = user_data.model_dump(
            exclude_unset=True
        )

        update_data.pop("password", None)

        for field, value in update_data.items():
            setattr(user, field, value)

        if hashed_password:
            user.hashed_password = hashed_password

        self.db.commit()
        self.db.refresh(user)

        return user

    def soft_delete(self, user: User) -> User:
        user.is_deleted = True

        self.db.commit()
        self.db.refresh(user)

        return user