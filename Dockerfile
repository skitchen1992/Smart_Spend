FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock* ./

# Настройка Poetry (не создавать виртуальное окружение, использовать системное)
RUN poetry config virtualenvs.create false

# Установка зависимостей
RUN poetry install --no-dev --no-interaction --no-ansi

# Копирование кода приложения
COPY . .

# Создание пользователя для запуска приложения
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Порт приложения
EXPOSE 8000

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
