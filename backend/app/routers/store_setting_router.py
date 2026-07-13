from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.store_setting import (
    StoreSettingCreate,
    StoreSettingResponse,
    StoreSettingUpdate,
)
from app.services.store_setting_service import StoreSettingService


router = APIRouter(
    prefix="/store-settings",
    tags=["Store Settings"],
)


@router.get(
    "",
    response_model=StoreSettingResponse,
)
def get_store_settings(
    db: Session = Depends(get_db),
):
    service = StoreSettingService(db)

    return service.get_current()


@router.post(
    "",
    response_model=StoreSettingResponse,
)
def create_store_settings(
    data: StoreSettingCreate,
    db: Session = Depends(get_db),
):
    service = StoreSettingService(db)

    return service.create(data)


@router.put(
    "/{store_setting_id}",
    response_model=StoreSettingResponse,
)
def update_store_settings(
    store_setting_id: int,
    data: StoreSettingUpdate,
    db: Session = Depends(get_db),
):
    service = StoreSettingService(db)

    return service.update(
        store_setting_id,
        data,
    )


@router.post(
    "/{store_setting_id}/logo",
    response_model=StoreSettingResponse,
)
async def upload_store_logo(
    store_setting_id: int,
    logo_file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    service = StoreSettingService(db)

    return await service.upload_logo(
        store_setting_id=store_setting_id,
        logo_file=logo_file,
    )