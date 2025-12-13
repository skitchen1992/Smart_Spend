# tests/test_groups.py
"""Тесты для app/modules/groups/router.py"""

from typing import Any
from unittest.mock import AsyncMock, patch, ANY

from fastapi import status

from app.modules.groups.schemas import (
    GroupCreate,
    GroupResponse,
    UserRead,
    GroupsResponseCreate,
    GroupUpdate,
)


class TestCreateGroup:
    """Тесты для POST /group/create (создание группы)"""

    def test_create_group_success(self, client: Any, mock_user: Any) -> None:
        """Успешное создание группы"""
        group_data = GroupCreate(name="Family budget")

        group_response = GroupsResponseCreate(
            id=1,
            owner_id=int(mock_user.id),
            members=[],
        )

        with patch("app.modules.groups.router.group_service") as mock_group_service:
            mock_group_service.create_group_service = AsyncMock(return_value=group_response)

            response = client.post("/group/create", json=group_data.model_dump())

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["success"] is True
            assert data["code"] == status.HTTP_200_OK
            assert "data" in data
            assert data["data"]["id"] == 1
            assert data["data"]["owner_id"] == int(mock_user.id)
            assert isinstance(data["data"]["members"], list)

            mock_group_service.create_group_service.assert_called_once()


class TestGroupDetails:
    """Тесты для GET /group/{group_id} (группа + участники)"""

    def test_get_group_with_members_success(self, client: Any, mock_user: Any) -> None:
        """Получение группы с участниками"""
        group_id = 1

        members = [
            UserRead(id=1, username="owner"),
            UserRead(id=2, username="member2"),
        ]

        group_response = GroupResponse(
            id=group_id,
            members=members,
        )

        with patch("app.modules.groups.router.group_service") as mock_group_service:
            mock_group_service.get_group_service = AsyncMock(return_value=group_response)

            response = client.get(f"/group/{group_id}")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["success"] is True
            assert data["code"] == status.HTTP_200_OK
            assert "data" in data
            assert data["data"]["id"] == group_id
            assert len(data["data"]["members"]) == 2
            assert data["data"]["members"][0]["username"] == "owner"

            mock_group_service.get_group_service.assert_called_once_with(
                db=ANY,
                group_id=group_id,
                id_user=int(mock_user.id),
            )


class TestUpdateGroup:
    """Тесты для PUT /group/{group_id}/update (обновление группы)"""

    def test_update_group_success(self, client: Any, mock_user: Any) -> None:
        group_id = 1
        update_data = GroupUpdate(name="New name")

        updated_group = GroupResponse(
            id=group_id,
            members=[],
        )

        with patch("app.modules.groups.router.group_service") as mock_group_service:
            mock_group_service.update_group_service = AsyncMock(return_value=updated_group)

            response = client.put(f"/group/{group_id}/update", json=update_data.model_dump())

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["success"] is True
            assert data["code"] == status.HTTP_200_OK
            assert data["data"]["id"] == group_id
            assert isinstance(data["data"]["members"], list)

            mock_group_service.update_group_service.assert_called_once_with(
                db=ANY,
                group_id=group_id,
                data=update_data,
                user_id=int(mock_user.id),
            )


class TestDeleteGroup:
    """Тесты для DELETE /group/{group_id} (удаление группы)"""

    def test_delete_group_success(self, client: Any, mock_user: Any) -> None:
        group_id = 1

        with patch("app.modules.groups.router.group_service") as mock_group_service:
            mock_group_service.delete_group_service = AsyncMock(
                return_value={"message": "Группа успешно удалена"}
            )

            response = client.delete(f"/group/{group_id}")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["success"] is True
            assert data["code"] == status.HTTP_200_OK
            assert data["data"]["message"] == "Группа успешно удалена"

            mock_group_service.delete_group_service.assert_called_once_with(
                db=ANY,
                group_id=group_id,
                id_user=int(mock_user.id),
            )
