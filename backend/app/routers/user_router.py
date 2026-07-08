from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
)

from app.services.user_service import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "",
    response_model=List[UserResponse],
)
def get_users(
    db: Session = Depends(get_db),
):
    service = UserService(db)

    return service.get_users()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    service = UserService(db)

    return service.get_user_by_id(
        user_id
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    service = UserService(db)

    return service.create_user(
        user_data
    )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
):
    service = UserService(db)

    return service.update_user(
        user_id,
        user_data
    )


@router.delete(
    "/{user_id}",
    response_model=UserResponse,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    service = UserService(db)

    return service.delete_user(
        user_id
    )