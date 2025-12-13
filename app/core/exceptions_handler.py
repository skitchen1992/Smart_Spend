from datetime import datetime, timezone
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import AppException
from app.core.dto.response import StandardResponse, ErrorDetail


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Обработчик исключений приложения с стандартизированным форматом ответа"""
    error_detail = ErrorDetail(message=str(exc.detail), code=exc.error_code)

    response: StandardResponse[None] = StandardResponse(
        success=False,
        code=exc.status_code,
        data=None,
        error=error_detail,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    return JSONResponse(status_code=exc.status_code, content=response.model_dump(exclude_none=True))


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Обработчик стандартных HTTP исключений FastAPI"""
    error_detail = ErrorDetail(message=str(exc.detail), code=None)

    response: StandardResponse[None] = StandardResponse(
        success=False,
        code=exc.status_code,
        data=None,
        error=error_detail,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    return JSONResponse(status_code=exc.status_code, content=response.model_dump(exclude_none=True))


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Обработчик ошибок SQLAlchemy"""
    error_detail = ErrorDetail(message="Database error", code=None)

    response: StandardResponse[None] = StandardResponse(
        success=False,
        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        data=None,
        error=error_detail,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump(exclude_none=True),
    )
