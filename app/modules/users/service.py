# Бизнес-логика пользователей
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.users.models import User
from app.modules.users.repository import user_repository
from app.modules.users.schemas import UserCreate
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import UserAlreadyExistsException, CredentialsException


class UserService:
    """Сервис для работы с пользователями"""

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
        """Получить пользователя по ID"""
        return await user_repository.get(db=db, id=user_id)

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        """Получить пользователя по email"""
        return await user_repository.get_by_email(db=db, email=email)

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
        """Получить пользователя по username"""
        return await user_repository.get_by_username(db=db, username=username)

    @staticmethod
    async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
        """Создать нового пользователя"""
        # Проверка на существование пользователя
        user = await user_repository.get_by_email(db=db, email=user_in.email)
        if user:
            raise UserAlreadyExistsException()

        user = await user_repository.get_by_username(db=db, username=user_in.username)
        if user:
            raise UserAlreadyExistsException(detail="Username already registered")

        hashed_password = get_password_hash(user_in.password)

        user_data = {
            "email": user_in.email,
            "username": user_in.username,
            "full_name": user_in.full_name,
            "hashed_password": hashed_password,
            "is_active": True,
        }

        return await user_repository.create(db=db, obj_in=user_data)

    @staticmethod
    async def change_password(
        db: AsyncSession, user: User, old_password: str, new_password: str
    ) -> User:
        """Сменить пароль пользователя"""
        # Проверяем текущий пароль
        if not user.hashed_password:
            raise CredentialsException(detail="Password not set for this user")

        if not verify_password(old_password, user.hashed_password):
            raise CredentialsException(detail="Incorrect current password")

        # Хэшируем новый пароль
        hashed_password = get_password_hash(new_password)

        # Обновляем пароль
        updated_user = await user_repository.update(
            db=db, db_obj=user, obj_in={"hashed_password": hashed_password}
        )

        return updated_user


# Создаем экземпляр сервиса для использования
user_service = UserService()
