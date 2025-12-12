from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions import NotFoundException, ValidationException
from .repository import group_repository
from .schemas import (
    GroupResponse,
    UserRead,
    GroupShort,
    UserGroupsResponse,
    GroupCreate,
    GroupsResponseCreate,
    GroupUpdate,
)
from ..group_members.service import group_member_service


class GroupService:
    async def get_group_service(
        self, db: AsyncSession, group_id: int, id_user: int
    ) -> GroupResponse:
        """
        Получить информацию о группе, если пользователь имеет к ней доступ.

        Args:
            db (AsyncSession): Асинхронная сессия БД.
            group_id (int): ID группы.
            id_user (int): ID пользователя, пытающегося получить группу.

        Returns:
            GroupResponse: Pydantic-схема с информацией о группе.

        Raises:
            HTTPException: Если пользователь не состоит в группе.
        """
        group = await group_repository.get_group(db, group_id, id_user)

        if not group:
            raise HTTPException(404, "Группа не найдена или у пользователя нет доступа к ней")

        members = [
            UserRead.model_validate({"id": user.id, "username": user.username})
            for user in group.members
        ]

        group_response = GroupResponse(id=int(group.id), members=members)

        return group_response

    async def get_users_groups_service(self, db: AsyncSession, user_id: int) -> UserGroupsResponse:
        """
        Получить список групп, в которых состоит пользователь.

        Args:
            db (AsyncSession): Асинхронная сессия БД.
            user_id (int): ID пользователя.

        Returns:
            UserGroupsResponse: Pydantic-обёртка со списком групп.

        Raises:
            HTTPException: Если пользователь не состоит ни в одной группе.
        """
        groups = await group_repository.get_users_groups(db, user_id)

        if not groups:
            raise HTTPException(404, "Пользователь не состоит ни в одной группе")

        groups_response = [GroupShort(id=int(group.id), name=str(group.name)) for group in groups]

        return UserGroupsResponse(groups=groups_response)

    async def create_group_service(
        self, db: AsyncSession, data: GroupCreate, owner_id: int
    ) -> GroupsResponseCreate:
        try:
            group = await group_repository.create_group(db, data, owner_id)

            try:
                await group_member_service.add_owner(
                    db=db, group_id=int(group.id), user_id=owner_id
                )
            except HTTPException as e:
                if e.status_code == 400 and "already exists" in str(e.detail):
                    # Владелец уже добавлен, продолжаем
                    pass
                else:
                    await db.rollback()
                    raise ValidationException(detail=str(e.detail))

            await db.refresh(group)

            group_with_membres = await group_repository.get_with_members(
                db=db, group_id=int(group.id)
            )
            if not group_with_membres:
                await db.rollback()
                raise NotFoundException(detail="Группа не найдена после создания")

            members = [
                UserRead(id=member.id, username=member.username)
                for member in group_with_membres.members
            ]

            return GroupsResponseCreate(
                id=int(group_with_membres.id),
                owner_id=int(group_with_membres.owner_id),
                members=members,
            )
        except (NotFoundException, ValidationException):
            # Пробрасываем кастомные исключения как есть
            raise
        except HTTPException as e:
            # Преобразуем HTTPException в кастомные исключения
            await db.rollback()
            if e.status_code == 404:
                raise NotFoundException(detail="Группа не найдена после создания")
            elif e.status_code == 400:
                raise ValidationException(detail=str(e.detail))
            raise e
        except IntegrityError:
            # Ошибки целостности данных БД
            await db.rollback()
            raise ValidationException(
                detail="Ошибка при создании группы. Возможно, группа с таким именем уже существует."
            )
        except SQLAlchemyError:
            # Другие ошибки БД
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Внутренняя ошибка сервера при создании группы",
            )
        except Exception:
            # Обработка неожиданных ошибок
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Произошла непредвиденная ошибка при создании группы",
            )

    async def update_group_service(
        self, db: AsyncSession, group_id: int, data: GroupUpdate, user_id: int
    ) -> GroupResponse:
        """
        Обновить информацию о группе.

        Args:
            db (AsyncSession): Асинхронная сессия БД.
            group_id (int): ID группы.
            data (GroupUpdate): Данные для обновления.
            user_id (int): ID пользователя (должен быть владельцем).

        Returns:
            GroupResponse: Обновлённая информация о группе.

        Raises:
            HTTPException: Если группа не найдена или пользователь не является владельцем.
        """
        # Обновляем группу
        updated_group = await group_repository.update_group(db, group_id, data, user_id)

        if not updated_group:
            raise HTTPException(
                status_code=404, detail="Group not found or you don't have permission to edit it"
            )

        # Формируем ответ
        members = [
            UserRead(id=member.id, username=member.username) for member in updated_group.members
        ]

        return GroupResponse(id=int(updated_group.id), members=members)

    async def delete_group_service(self, db: AsyncSession, group_id: int, id_user: int) -> dict:
        """
        Удалить группу (сервисный слой).

        Args:
            db (AsyncSession): Асинхронная сессия БД.
            group_id (int): ID группы.
            id_user (int): ID пользователя.

        Returns:
            dict: Сообщение об успешном удалении.

        Raises:
            HTTPException: Если группа не найдена, пользователь не владелец
                          или в группе есть другие участники.
        """
        try:
            deleted = await group_repository.delete_group(db, group_id, id_user)

            if not deleted:
                raise HTTPException(
                    status_code=404,
                    detail="Группа не найдена или у пользователя нет доступа к удалению",
                )

            return {"message": "Группа успешно удалена"}

        except HTTPException as e:
            raise e


group_service = GroupService()
