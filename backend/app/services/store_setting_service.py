from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.store_setting_repository import StoreSettingRepository

from app.schemas.store_setting import (
    StoreSettingCreate,
    StoreSettingUpdate,
)


class StoreSettingService:

    def __init__(self, db: Session):
        self.repository = StoreSettingRepository(db)

    def get_current(self):

        store_setting = self.repository.get_current()

        if not store_setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store settings not found"
            )

        return store_setting

    def create(
        self,
        data: StoreSettingCreate
    ):

        existing = self.repository.get_current()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Store settings already exists"
            )

        return self.repository.create(data)

    def update(
        self,
        store_setting_id: int,
        data: StoreSettingUpdate
    ):

        store_setting = self.repository.get_by_id(
            store_setting_id
        )

        if not store_setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store settings not found"
            )

        return self.repository.update(
            store_setting,
            data
        )