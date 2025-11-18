# Бизнес-логика пользователей
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.users.models import User
from app.modules.users.repository import user_repository


class UserService:
    """Сервис для работы с пользователями"""

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
        """Получить пользователя по ID"""
        return await user_repository.get(db=db, id=user_id)


# Создаем экземпляр сервиса для использования
user_service = UserService()
