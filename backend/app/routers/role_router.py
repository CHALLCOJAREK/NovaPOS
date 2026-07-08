from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.role import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
)

from app.services.role_service import RoleService


router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)


@router.get(
    "",
    response_model=List[RoleResponse],
)
def get_roles(
    db: Session = Depends(get_db),
):
    service = RoleService(db)

    return service.get_roles()


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
):
    service = RoleService(db)

    return service.get_role_by_id(
        role_id
    )


@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
):
    service = RoleService(db)

    return service.create_role(
        role_data
    )


@router.put(
    "/{role_id}",
    response_model=RoleResponse,
)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
):
    service = RoleService(db)

    return service.update_role(
        role_id,
        role_data
    )


@router.delete(
    "/{role_id}",
    response_model=RoleResponse,
)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
):
    service = RoleService(db)

    return service.delete_role(
        role_id
    )