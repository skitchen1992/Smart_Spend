"""Тесты для app/modules/group_members/router.py"""

from typing import Any
from unittest.mock import AsyncMock, patch, ANY

from fastapi import status

from app.modules.group_members.schemas import (
    GroupMemberCreate,
    GroupMemberDelete,
    GroupMemberResponse,
)


class TestAddMember:
    """Тесты для POST /group-members/add_member"""

    def test_add_member_success(self, client: Any, mock_user: Any) -> None:
        """Успешное добавление участника в группу"""
        member_data = GroupMemberCreate(group_id=1, user_id=2)

        expected_response = GroupMemberResponse(
            status="success",
            message="Участник успешно добавлен в группу",
            group_id=1,
            user_id=2,
        )

        with patch("app.modules.group_members.router.group_member_service") as mock_service:
            mock_service.add = AsyncMock(return_value=expected_response)

            response = client.post("/group-members/add_member", json=member_data.model_dump())

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["success"] is True
            assert data["code"] == status.HTTP_200_OK
            assert "data" in data
            assert data["data"]["status"] == "success"
            assert data["data"]["group_id"] == 1
            assert data["data"]["user_id"] == 2

            mock_service.add.assert_called_once_with(
                db=ANY,
                group_id=1,
                user_id=2,
                requester_id=mock_user.id,
            )


class TestRemoveMember:
    """Тесты для DELETE /group-members/delete"""

    def test_remove_member_success(self, client: Any, mock_user: Any) -> None:
        """Успешное удаление участника из группы"""
        import json

        member_data = GroupMemberDelete(group_id=1, user_id=2)

        expected_response = GroupMemberResponse(
            status="success",
            message="Участник успешно удален из группы",
            group_id=1,
            user_id=2,
        )

        with patch("app.modules.group_members.router.group_member_service") as mock_service:
            mock_service.remove = AsyncMock(return_value=expected_response)

            # Используем request() для DELETE с телом запроса
            response = client.request(
                "DELETE",
                "/group-members/delete",
                content=json.dumps(member_data.model_dump()),
                headers={"Content-Type": "application/json"},
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["success"] is True
            assert data["code"] == status.HTTP_200_OK
            assert "data" in data
            assert data["data"]["status"] == "success"
            assert data["data"]["group_id"] == 1
            assert data["data"]["user_id"] == 2

            mock_service.remove.assert_called_once_with(
                db=ANY,
                group_id=1,
                user_id=2,
                requester_id=mock_user.id,
            )
