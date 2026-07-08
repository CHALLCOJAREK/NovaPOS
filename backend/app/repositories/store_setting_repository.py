from sqlalchemy.orm import Session

from app.models.store_setting import StoreSetting
from app.schemas.store_setting import (
    StoreSettingCreate,
    StoreSettingUpdate,
)


class StoreSettingRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_current(self) -> StoreSetting | None:
        return (
            self.db.query(StoreSetting)
            .filter(
                StoreSetting.is_deleted == False,
                StoreSetting.is_active == True,
            )
            .first()
        )

    def get_by_id(
        self,
        store_setting_id: int
    ) -> StoreSetting | None:
        return (
            self.db.query(StoreSetting)
            .filter(
                StoreSetting.id == store_setting_id,
                StoreSetting.is_deleted == False,
            )
            .first()
        )

    def create(
        self,
        data: StoreSettingCreate
    ) -> StoreSetting:

        store_setting = StoreSetting(
            **data.model_dump()
        )

        self.db.add(store_setting)
        self.db.commit()
        self.db.refresh(store_setting)

        return store_setting

    def update(
        self,
        store_setting: StoreSetting,
        data: StoreSettingUpdate
    ) -> StoreSetting:

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(
                store_setting,
                field,
                value
            )

        self.db.commit()
        self.db.refresh(store_setting)

        return store_setting