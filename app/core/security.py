from datetime import datetime, timedelta
from typing import Optional, Any
import hashlib
from uuid import uuid4
from jose import JWTError, jwt  # type: ignore[import-untyped]
from passlib.context import CryptContext  # type: ignore[import-untyped]
from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return bool(pwd_context.verify(plain_password, hashed_password))


def get_password_hash(password: str) -> str:
    """Хэширование пароля"""
    return str(pwd_context.hash(password))


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return str(encoded_jwt)


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """Декодирование JWT токена"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return dict(payload) if payload else None
    except JWTError:
        return None


def create_refresh_token(
    data: dict[str, Any], expires_delta: Optional[timedelta] = None, jti: str | None = None
) -> tuple[str, str]:
    """Создание JWT refresh токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token_jti = jti or str(uuid4())
    to_encode.update({"exp": expire, "type": "refresh", "jti": token_jti})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return str(encoded_jwt), token_jti


def hash_token(token: str) -> str:
    """Возвращает SHA256-хэш токена для безопасного хранения"""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
