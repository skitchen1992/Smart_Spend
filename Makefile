.PHONY: help install run dev test lint format migrate migrate-create clean stop kill-port docker-build docker-up docker-down docker-logs docker-restart docker-shell docker-migrate docker-migrate-create docker-test docker-clean

help: ## Показать доступные команды
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

stop: ## Остановить запущенное приложение
	@echo "Остановка процессов uvicorn..."
	@pkill -f "uvicorn app.main:app" || echo "Процессы не найдены"

kill-port: ## Освободить порт 8000
	@echo "Освобождение порта 8000..."
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "Порт 8000 свободен"

install: ## Установить зависимости
	poetry install

run: ## Запустить приложение
	poetry run uvicorn app.main:app --reload

dev: ## Запустить в режиме разработки (с автоперезагрузкой)
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

prod: ## Запустить в production режиме
	poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

test: ## Запустить тесты
	poetry run pytest

test-watch: ## Запустить тесты в режиме watch
	poetry run pytest-watch

lint: ## Проверить код линтером
	poetry run ruff check app/

format: ## Отформатировать код
	poetry run black app/
	poetry run ruff check --fix app/

type-check: ## Проверить типы
	poetry run mypy app/

check: lint type-check ## Запустить все проверки (lint + type-check)

migrate: ## Применить миграции БД
	poetry run alembic upgrade head

migrate-create: ## Создать новую миграцию (использовать: make migrate-create MESSAGE="описание")
	poetry run alembic revision --autogenerate -m "$(MESSAGE)"

migrate-downgrade: ## Откатить последнюю миграцию
	poetry run alembic downgrade -1

shell: ## Активировать виртуальное окружение
	poetry shell

clean: ## Очистить кэш и временные файлы
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	rm -rf .ruff_cache

db-reset: ## Сбросить БД и применить миграции заново
	rm -f smart_spend.db
	poetry run alembic upgrade head

# Docker команды
docker-build: ## Собрать Docker образ
	@if [ ! -f .env ]; then \
		echo "Ошибка: файл .env не найден!"; \
		echo "Создайте файл .env перед запуском Docker."; \
		exit 1; \
	fi
	docker compose build

docker-up: ## Запустить контейнеры
	@if [ ! -f .env ]; then \
		echo "Ошибка: файл .env не найден!"; \
		echo "Создайте файл .env перед запуском Docker."; \
		exit 1; \
	fi
	docker compose up -d

docker-down: ## Остановить контейнеры
	docker compose down

docker-logs: ## Показать логи контейнеров
	docker compose logs -f

docker-restart: ## Перезапустить контейнеры
	@if [ ! -f .env ]; then \
		echo "Ошибка: файл .env не найден!"; \
		echo "Создайте файл .env перед запуском Docker."; \
		exit 1; \
	fi
	docker compose restart

docker-shell: ## Войти в контейнер приложения
	docker compose exec app bash

docker-migrate: ## Применить миграции в Docker
	docker compose exec app poetry run alembic upgrade head

docker-migrate-create: ## Создать миграцию в Docker (использовать: make docker-migrate-create MESSAGE="описание")
	docker compose exec app poetry run alembic revision --autogenerate -m "$(MESSAGE)"

docker-test: ## Запустить тесты в Docker
	docker compose exec app poetry run pytest

docker-clean: ## Остановить и удалить контейнеры, volumes и образы
	docker compose down -v --rmi all
