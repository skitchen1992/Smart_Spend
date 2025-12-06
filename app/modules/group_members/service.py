from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .repository import group_member_repository
from .schemas import GroupMemberResponse
from ..groups.repository import group_repository  # Импортируем репозиторий групп


class GroupMemberService:

    async def add_owner(self, db: AsyncSession, group_id: int, user_id: int):
        exists = await group_member_repository.exists(db, group_id, user_id)
        if exists:
            raise HTTPException(400, "User already in group")

        return await group_member_repository.create(
            db,
            {"group_id": group_id, "user_id": user_id}
        )

    async def add(self, db: AsyncSession, group_id: int, user_id: int, requester_id: int) -> GroupMemberResponse:
        """
        Добавить участника в группу.

        Args:
            db: Асинхронная сессия БД
            group_id: ID группы
            user_id: ID пользователя для добавления
            requester_id: ID пользователя, который делает запрос (должен быть владельцем)
        """
        # Проверяем, является ли requester владельцем группы
        group = await group_repository.get_group_by_id(db, group_id)
        if not group:
            raise HTTPException(404, "Group not found")

        if group.owner_id != requester_id:
            raise HTTPException(403, "Only group owner can add members")

        # Проверяем, не является ли user_id самим владельцем (он уже должен быть в группе)
        if user_id == requester_id:
            raise HTTPException(400, "Owner is already a member")

        # Проверяем, не состоит ли пользователь уже в группе
        exists = await group_member_repository.exists(db, group_id, user_id)
        if exists:
            raise HTTPException(400, "User already in group")

        # Добавляем участника в группу
        await group_member_repository.create(
             db,
            {"group_id": group_id, "user_id": user_id}
        )

        # Возвращаем Pydantic модель вместо SQLAlchemy объекта
        return GroupMemberResponse(
            status="success",
            message="User added to group",
            group_id=group_id,
            user_id=user_id
        )

    async def remove(self, db: AsyncSession, group_id: int, user_id: int, requester_id: int) -> GroupMemberResponse:
        """
        Удалить участника из группы.

        Args:
            db: Асинхронная сессия БД
            group_id: ID группы
            user_id: ID пользователя для удаления
            requester_id: ID пользователя, который делает запрос (должен быть владельцем)
        """
        # Проверяем, является ли requester владельцем группы
        group = await group_repository.get_group_by_id(db, group_id)
        if not group:
            raise HTTPException(404, "Group not found")

        if group.owner_id != requester_id:
            raise HTTPException(403, "Only group owner can remove members")

        # Проверяем, не пытается ли владелец удалить себя
        if user_id == requester_id:
            raise HTTPException(400, "Owner cannot remove themselves from group")

        # Проверяем, состоит ли пользователь в группе
        exists = await group_member_repository.exists(db, group_id, user_id)
        if not exists:
            raise HTTPException(400, "User not in group")

        await group_member_repository.remove(db, group_id, user_id)

        return GroupMemberResponse(
            status="success",
            message="User removed from group",
            group_id=group_id,
            user_id=user_id
        )


group_member_service = GroupMemberService()