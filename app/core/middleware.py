from datetime import datetime
from typing import Callable, Any, Awaitable
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse, Response
from app.core.dto.response import StandardResponse
import json
import logging


class StandardResponseMiddleware(BaseHTTPMiddleware):
    """Middleware для форматирования успешных ответов в стандартизированный формат"""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response: Response = await call_next(request)

        # Обрабатываем только успешные ответы (2xx)
        if 200 <= response.status_code < 300:
            # Пропускаем health check и root endpoint, а также документацию
            if request.url.path in ["/", "/health", "/docs", "/openapi.json", "/redoc"]:
                return response

            # Пропускаем streaming responses
            if isinstance(response, StreamingResponse):
                return response

            try:
                data = None

                # Для JSONResponse используем body напрямую
                if isinstance(response, JSONResponse):
                    try:
                        # Получаем body из JSONResponse
                        # JSONResponse имеет свойство body, которое возвращает bytes
                        body: bytes = (
                            response.body if hasattr(response, "body") and response.body else b""
                        )

                        # Проверяем, не является ли ответ уже стандартизированным
                        content = body.decode() if body else "{}"
                        if '"success"' in content and '"code"' in content:
                            return response

                        # Парсим JSON из ответа
                        data = json.loads(content) if body else None
                        logging.debug(f"Parsed data: {data}")
                    except Exception as e:
                        logging.error(f"Error reading JSONResponse body: {e}", exc_info=True)
                        return Response(
                            content=response.body if hasattr(response, "body") else b"",
                            status_code=response.status_code,
                            headers=dict(response.headers),
                            media_type=response.media_type,
                        )
                else:
                    # Для других типов ответов читаем body_iterator
                    # body_iterator существует в runtime у всех Response в Starlette
                    body = b""
                    async for chunk in response.body_iterator:  # type: ignore[attr-defined]
                        body += chunk

                    try:
                        data = json.loads(body.decode()) if body else None
                    except json.JSONDecodeError:
                        # Если не JSON, создаем новый Response без Content-Length
                        headers = {
                            k: v
                            for k, v in response.headers.items()
                            if k.lower() != "content-length"
                        }
                        return Response(
                            content=body,
                            status_code=response.status_code,
                            media_type=response.media_type,
                            headers=headers,
                        )

                # Форматируем в стандартизированный формат
                standard_response: StandardResponse[Any] = StandardResponse(
                    success=True,
                    code=response.status_code,
                    data=data,
                    error=None,
                    timestamp=datetime.utcnow().isoformat() + "Z",
                )

                # Создаем новый JSONResponse - FastAPI автоматически установит правильный Content-Length
                response_content = standard_response.model_dump(exclude_none=True)
                return JSONResponse(content=response_content, status_code=response.status_code)
            except Exception as e:
                # В случае ошибки возвращаем оригинальный ответ
                logging.error(f"Error in StandardResponseMiddleware: {e}", exc_info=True)
                return response

        return response
