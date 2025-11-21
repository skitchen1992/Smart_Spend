from datetime import datetime
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
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
        timestamp=datetime.utcnow().isoformat() + "Z",
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
        timestamp=datetime.utcnow().isoformat() + "Z",
    )

    return JSONResponse(status_code=exc.status_code, content=response.model_dump(exclude_none=True))
