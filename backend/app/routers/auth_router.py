from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserLogin
from app.schemas.auth import AuthLoginResponse
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
    "/login",
    response_model=AuthLoginResponse,
)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    return service.login(
        login_data
    )