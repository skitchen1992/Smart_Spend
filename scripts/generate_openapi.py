"""Скрипт для генерации файлов swagger.json и swagger.yaml из OpenAPI схемы FastAPI"""
import json
import os
from pathlib import Path

import yaml

# Устанавливаем фиктивные значения для обязательных переменных окружения
# перед импортом приложения, чтобы избежать ошибок при инициализации
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost:5432/db"
if "SECRET_KEY" not in os.environ:
    # Генерируем фиктивный секретный ключ длиной 32+ символов
    os.environ["SECRET_KEY"] = "fake-secret-key-for-openapi-generation-only-" + "x" * 32

from app.main import app

# Получаем OpenAPI схему из FastAPI приложения
openapi_schema = app.openapi()

# Определяем пути для сохранения файлов
project_root = Path(__file__).parent.parent
swagger_json_path = project_root / "swagger.json"
swagger_yaml_path = project_root / "swagger.yaml"

# Сохраняем в JSON
with open(swagger_json_path, "w", encoding="utf-8") as f:
    json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

print(f"✅ swagger.json создан: {swagger_json_path}")

# Сохраняем в YAML
with open(swagger_yaml_path, "w", encoding="utf-8") as f:
    yaml.dump(openapi_schema, f, allow_unicode=True, sort_keys=False)

print(f"✅ swagger.yaml создан: {swagger_yaml_path}")
