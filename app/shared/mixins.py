"""
Повторно используемые классы и миксины
"""

from typing import TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.shared.base_model import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class CRUDMixin(Generic[ModelType]):
    """Базовый CRUD миксин для репозиториев (асинхронный)"""

    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> ModelType | None:
        """Получить по ID"""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Получить список с пагинацией"""
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: dict) -> ModelType:
        """Создать новый объект"""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.flush()  # Flush для получения ID, commit делается в get_db()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: ModelType, obj_in: dict) -> ModelType:
        """Обновить объект"""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        await db.flush()  # Flush для применения изменений, commit делается в get_db()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: int) -> ModelType | None:
        """Удалить объект"""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        obj = result.scalar_one_or_none()
        if obj:
            db.delete(obj)  # type: ignore[unused-coroutine]  # delete - синхронный метод, но работает в async контексте
            await db.flush()  # Flush для применения изменений, commit делается в get_db()
        return obj
