from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.exceptions import CredentialsException
from app.modules.auth.service import auth_service

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Возвращает текущего пользователя, извлекая его из access токена."""
    if not credentials:
        raise CredentialsException(detail="Authorization header missing")

    return await auth_service.get_user_from_token(db, credentials.credentials)
