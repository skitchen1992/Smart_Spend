from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.exceptions import CredentialsException
from app.core.dto.response import StandardResponse, success_response
from app.modules.auth.schemas import Token, Login, RefreshTokenRequest
from app.modules.auth.service import auth_service
from app.modules.users.schemas import UserCreate
from app.modules.users.service import user_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=StandardResponse[Token],
    status_code=status.HTTP_201_CREATED,
)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Регистрация нового пользователя"""
    user = await user_service.create_user(db=db, user_in=user_in)
    tokens = await auth_service.generate_tokens(db=db, user=user)
    return success_response(data=tokens)


@router.post("/login", response_model=StandardResponse[Token])
async def login(login_data: Login, db: AsyncSession = Depends(get_db)):
    """
    Авторизация пользователя.
    Возвращает access и refresh токены.
    """
    user = await auth_service.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise CredentialsException(detail="Incorrect username or password")

    tokens = await auth_service.generate_tokens(db=db, user=user)
    return success_response(data=tokens)


@router.post("/refresh", response_model=StandardResponse[Token])
async def refresh_token(refresh_data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """
    Обновление токенов с помощью refresh токена.
    """
    tokens = await auth_service.refresh_access_token(db, refresh_data.refresh_token)
    return success_response(data=tokens)
