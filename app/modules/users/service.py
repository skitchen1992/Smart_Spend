# Бизнес-логика пользователей
from sqlalchemy.orm import Session
from app.modules.users.models import User
from app.modules.users.repository import user_repository


class UserService:
    """Сервис для работы с пользователями"""

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User | None:
        """Получить пользователя по ID"""
        return user_repository.get(db=db, id=user_id)


# Создаем экземпляр сервиса для использования
user_service = UserService()
