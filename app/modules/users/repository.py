# CRUD и работа с БД для пользователей
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.users.models import User
from app.shared.mixins import CRUDMixin


class UserRepository(CRUDMixin[User]):
    """Репозиторий для работы с пользователями"""

    def __init__(self) -> None:
        super().__init__(User)

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        """Получить пользователя по username"""
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """Получить пользователя по email"""
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()


# Создаем экземпляр репозитория для использования
user_repository = UserRepository()
