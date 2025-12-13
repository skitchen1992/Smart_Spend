from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .repository import group_member_repository
from .schemas import GroupMemberResponse
from .models import GroupMember
from ..groups.repository import group_repository  # Импортируем репозиторий групп
from ..users.service import user_service


class GroupMemberService:
    async def user_in_any_group(self, db: AsyncSession, user_id: int) -> bool:
        """
        Проверить, состоит ли пользователь в какой-либо группе.

        Args:
            db: Асинхронная сессия БД
            user_id: ID пользователя

        Returns:
            bool: True если пользователь состоит в какой-либо группе, False иначе
        """
        return await group_member_repository.user_in_any_group(db, user_id)

    async def add_owner(self, db: AsyncSession, group_id: int, user_id: int) -> GroupMember:
        exists = await group_member_repository.exists(db, group_id, user_id)
        if exists:
            raise HTTPException(400, "Пользователь уже в группе")

        return await group_member_repository.create(db, {"group_id": group_id, "user_id": user_id})

    async def add(
        self, db: AsyncSession, group_id: int, user_id: int, requester_id: int
    ) -> GroupMemberResponse:
        """
        Добавить участника в группу.

        Бизнес-правило: Один пользователь может состоять только в одной группе.
        Это ограничение реализовано для семейного бюджета.

        Args:
            db: Асинхронная сессия БД
            group_id: ID группы
            user_id: ID пользователя для добавления
            requester_id: ID пользователя, который делает запрос (должен быть владельцем)
        """
        try:
            # Проверяем, является ли requester владельцем группы
            group = await group_repository.get_group_by_id(db, group_id)
            if not group:
                raise HTTPException(404, "Группа не найдена")

            if group.owner_id != requester_id:
                raise HTTPException(403, "Только владелец группы может добавлять участников")

            # Проверяем, не является ли user_id самим владельцем (он уже должен быть в группе)
            if user_id == requester_id:
                raise HTTPException(400, "Владелец уже является участником")

            user_exists = await user_service.get_user_by_id(db, user_id)
            if not user_exists:
                raise HTTPException(400, "Пользователь не существует")

            # Бизнес-правило: проверяем, не состоит ли пользователь уже в какой-либо группе
            # Один пользователь может состоять только в одной группе (семейный бюджет)
            user_in_any_group = await group_member_repository.user_in_any_group(db, user_id)
            if user_in_any_group:
                raise HTTPException(
                    400,
                    "Пользователь уже состоит в другой группе. Один пользователь может состоять только в одной группе.",
                )

            # Проверяем, не состоит ли пользователь уже в этой группе (дополнительная проверка)
            exists = await group_member_repository.exists(db, group_id, user_id)
            if exists:
                raise HTTPException(400, "Пользователь уже в группе")

            # Добавляем участника в группу
            await group_member_repository.create(db, {"group_id": group_id, "user_id": user_id})
            await db.commit()

            # Возвращаем Pydantic модель вместо SQLAlchemy объекта
            return GroupMemberResponse(
                status="success",
                message="Пользователь добавлен в группу",
                group_id=group_id,
                user_id=user_id,
            )
        except HTTPException:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise HTTPException(500, "Ошибка при добавлении участника в группу")

    async def remove(
        self, db: AsyncSession, group_id: int, user_id: int, requester_id: int
    ) -> GroupMemberResponse:
        """
        Удалить участника из группы.

        Args:
            db: Асинхронная сессия БД
            group_id: ID группы
            user_id: ID пользователя для удаления
            requester_id: ID пользователя, который делает запрос (должен быть владельцем)
        """
        try:
            # Проверяем, является ли requester владельцем группы
            group = await group_repository.get_group_by_id(db, group_id)
            if not group:
                raise HTTPException(404, "Группа не найдена")

            if group.owner_id != requester_id:
                raise HTTPException(403, "Только владелец группы может удалять участников")

            # Проверяем, не пытается ли владелец удалить себя
            if user_id == requester_id:
                raise HTTPException(400, "Владелец не может удалить себя из группы")

            # Проверяем, состоит ли пользователь в группе
            exists = await group_member_repository.exists(db, group_id, user_id)
            if not exists:
                raise HTTPException(400, "Пользователь не состоит в группе")

            await group_member_repository.remove(db, group_id, user_id)
            await db.commit()

            return GroupMemberResponse(
                status="success",
                message="Пользователь удален из группы",
                group_id=group_id,
                user_id=user_id,
            )
        except HTTPException:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise HTTPException(500, "Ошибка при удалении участника из группы")


group_member_service = GroupMemberService()
