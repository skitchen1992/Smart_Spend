# Эндпоинты FastAPI для пользователей
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.modules.users.service import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получить пользователя по ID
    """
    user = await user_service.get_user_by_id(db=db, user_id=user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user
