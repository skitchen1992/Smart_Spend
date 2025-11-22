# Эндпоинты FastAPI для пользователей
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.exceptions import NotFoundException
from app.core.dto.response import StandardResponse, success_response
from app.modules.users.service import user_service
from app.modules.users.schemas import UserResponse
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=StandardResponse[UserResponse])
async def get_me(current_user=Depends(get_current_user)) -> StandardResponse[UserResponse]:
    user_data = UserResponse.model_validate(current_user)
    return success_response(data=user_data)


@router.get("/{user_id}", response_model=StandardResponse[UserResponse])
async def get_user(
    user_id: int, db: AsyncSession = Depends(get_db)
) -> StandardResponse[UserResponse]:
    user = await user_service.get_user_by_id(db=db, user_id=user_id)

    if not user:
        raise NotFoundException(detail="Пользователь не найден")

    # Возвращаем данные в стандартизированном формате
    user_data = UserResponse.model_validate(user)
    return success_response(data=user_data)
