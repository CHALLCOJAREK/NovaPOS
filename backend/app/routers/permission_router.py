from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.permission import (
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse,
)

from app.services.permission_service import PermissionService


router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
)


@router.get(
    "",
    response_model=List[PermissionResponse],
)
def get_permissions(
    db: Session = Depends(get_db),
):
    service = PermissionService(db)

    return service.get_permissions()


@router.get(
    "/{permission_id}",
    response_model=PermissionResponse,
)
def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
):
    service = PermissionService(db)

    return service.get_permission_by_id(
        permission_id
    )


@router.post(
    "",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_permission(
    permission_data: PermissionCreate,
    db: Session = Depends(get_db),
):
    service = PermissionService(db)

    return service.create_permission(
        permission_data
    )


@router.put(
    "/{permission_id}",
    response_model=PermissionResponse,
)
def update_permission(
    permission_id: int,
    permission_data: PermissionUpdate,
    db: Session = Depends(get_db),
):
    service = PermissionService(db)

    return service.update_permission(
        permission_id,
        permission_data
    )


@router.delete(
    "/{permission_id}",
    response_model=PermissionResponse,
)
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
):
    service = PermissionService(db)

    return service.delete_permission(
        permission_id
    )