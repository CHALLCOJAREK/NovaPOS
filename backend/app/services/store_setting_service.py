from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
import base64
import mimetypes
from app.repositories.store_setting_repository import StoreSettingRepository
from app.schemas.store_setting import (
    StoreSettingCreate,
    StoreSettingUpdate,
)


class StoreSettingService:
    ALLOWED_LOGO_CONTENT_TYPES = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/webp": ".webp",
    }

    MAX_LOGO_SIZE_BYTES = 5 * 1024 * 1024

    def __init__(self, db: Session):
        self.repository = StoreSettingRepository(db)

    def get_current(self):
        store_setting = self.repository.get_current()

        if not store_setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuración de tienda no encontrada",
            )

        return store_setting

    def create(
        self,
        data: StoreSettingCreate,
    ):
        existing = self.repository.get_current()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La configuración de tienda ya existe",
            )

        return self.repository.create(data)

    def update(
        self,
        store_setting_id: int,
        data: StoreSettingUpdate,
    ):
        store_setting = self.repository.get_by_id(
            store_setting_id
        )

        if not store_setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuración de tienda no encontrada",
            )

        return self.repository.update(
            store_setting,
            data,
        )

    async def upload_logo(
        self,
        store_setting_id: int,
        logo_file: UploadFile,
    ):
        store_setting = self.repository.get_by_id(
            store_setting_id
        )

        if not store_setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuración de tienda no encontrada",
            )

        file_extension = self.ALLOWED_LOGO_CONTENT_TYPES.get(
            logo_file.content_type or ""
        )

        if file_extension is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Formato de logo no permitido. "
                    "Use PNG, JPG, JPEG o WEBP."
                ),
            )

        file_content = await logo_file.read()

        if not file_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo del logo está vacío",
            )

        if len(file_content) > self.MAX_LOGO_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El logo no puede superar los 5 MB",
            )

        logos_directory = (
            Path(settings.UPLOAD_PATH)
            / "logos"
        ).resolve()

        logos_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        filename = (
            f"store_logo_{uuid4().hex[:8]}"
            f"{file_extension}"
        )

        logo_path = logos_directory / filename

        try:
            logo_path.write_bytes(file_content)
        except OSError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo guardar el logo de la tienda",
            ) from exc
        finally:
            await logo_file.close()

        relative_logo_path = (
            Path("logos")
            / filename
        ).as_posix()

        previous_logo_path = store_setting.logo_path

        try:
            updated_store_setting = self.repository.update(
                store_setting,
                StoreSettingUpdate(
                    logo_path=relative_logo_path
                ),
            )
        except Exception:
            if logo_path.exists():
                logo_path.unlink()

            raise

        self._delete_previous_logo(
            previous_logo_path=previous_logo_path,
            current_logo_path=logo_path,
            logos_directory=logos_directory,
        )

        return updated_store_setting

    @staticmethod
    def resolve_logo_path(
        logo_path: str | None,
    ) -> Path | None:
        if not logo_path:
            return None

        resolved_logo_path = (
            Path(settings.UPLOAD_PATH)
            / logo_path
        ).resolve()

        if not resolved_logo_path.is_file():
            return None

        return resolved_logo_path

    @staticmethod
    def get_logo_uri(
        logo_path: str | None,
    ) -> str | None:
        resolved_logo_path = StoreSettingService.resolve_logo_path(
            logo_path
        )

        if resolved_logo_path is None:
            return None

        mime_type, _ = mimetypes.guess_type(
            resolved_logo_path.name
        )

        if mime_type not in {
            "image/png",
            "image/jpeg",
            "image/webp",
        }:
            return None

        try:
            encoded_logo = base64.b64encode(
                resolved_logo_path.read_bytes()
            ).decode("ascii")
        except OSError:
            return None

        return (
            f"data:{mime_type};base64,"
            f"{encoded_logo}"
        )

    @staticmethod
    def _delete_previous_logo(
        previous_logo_path: str | None,
        current_logo_path: Path,
        logos_directory: Path,
    ) -> None:
        if not previous_logo_path:
            return

        previous_file = (
            Path(settings.UPLOAD_PATH)
            / previous_logo_path
        ).resolve()

        try:
            previous_file.relative_to(logos_directory)
        except ValueError:
            return

        if (
            previous_file != current_logo_path
            and previous_file.is_file()
        ):
            previous_file.unlink()