# CRUD и работа с БД для пользователей
from sqlalchemy.orm import Session
from app.modules.users.models import User
from app.shared.mixins import CRUDMixin


class UserRepository(CRUDMixin[User]):
    """Репозиторий для работы с пользователями"""

    def __init__(self):
        super().__init__(User)

    def get_by_username(self, db: Session, username: str) -> User | None:
        """Получить пользователя по username"""
        return db.query(User).filter(User.username == username).first()


# Создаем экземпляр репозитория для использования
user_repository = UserRepository()
