# Auth Service FastAPI

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-7-red?logo=redis)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)

> Готовый шаблон FastAPI-сервиса с аутентификацией, JWT и feature-based архитектурой.  
> Клонируй — и сразу пиши бизнес-логику, не тратя время на базовую инфраструктуру.

---

## 📋 Содержание

- [О проекте](#-о-проекте)
- [Технологии](#-технологии)
- [Структура проекта](#-структура-проекта)
- [Быстрый старт](#-быстрый-старт)
- [Переменные окружения](#-переменные-окружения)
- [Миграции](#-миграции)
- [Тестирование](#-тестирование)
- [Использование как шаблон](#-использование-как-шаблон)

---

## 🗂 О проекте

**Auth Service** — это production-ready шаблон FastAPI-сервиса, который решает задачу, возникающую в начале почти каждого backend-проекта: настройка регистрации, авторизации, JWT-токенов и базовой инфраструктуры занимает дни, хотя реализация везде одинаковая.

### 💡 Проблема

Каждый новый сервис начинается одинаково: настроить FastAPI, подключить PostgreSQL и Redis, реализовать регистрацию/авторизацию, придумать структуру папок, настроить Docker, написать хотя бы базовые тесты. Это рутина, которая отнимает время и никак не связана с реальной задачей проекта.

### ✅ Решение

Этот шаблон содержит всё необходимое из коробки — достаточно клонировать репозиторий, переименовать модули под свой домен и сразу писать бизнес-логику. Auth и инфраструктура уже работают.

**Что выделяет этот шаблон:**
- 🏗 **Feature-based структура** — код организован по фичам, а не по типам файлов. Легко масштабируется: добавляешь новый модуль в `src/`, подключаешь в `main.py` — всё
- 🔐 **Полноценный JWT** — access + refresh токены, хранение refresh в Redis, возможность инвалидации
- 🧪 **Три уровня тестов** — unit, functional и integration тесты как образец для новых модулей
- ⚡ **uv** — современный менеджер зависимостей, в разы быстрее pip
- 🐳 **Docker из коробки** — одна команда поднимает приложение + Postgres + Redis

### 🎯 Для кого

| Сценарий | Описание |
|---|---|
| Новый микросервис | Быстрый старт без написания auth с нуля |
| Учебный проект | Пример правильной структуры FastAPI-приложения |
| Прототип / MVP | Рабочая база уже на первый день |

---

## 🛠 Технологии

| Слой | Стек |
|---|---|
| Backend | Python 3.11, FastAPI |
| База данных | PostgreSQL 15, SQLAlchemy (async) |
| Кэш / токены | Redis |
| Миграции | Alembic |
| Аутентификация | JWT (access + refresh) |
| Тестирование | Pytest (unit / functional / integration) |
| Зависимости | uv |
| Инфраструктура | Docker, docker-compose |

---

## 📁 Структура проекта

Feature-based архитектура: каждая фича — изолированный модуль со своими роутерами, схемами и сервисами.

```
src/
├── auth/               # JWT: выдача, обновление, отзыв токенов
│   ├── router.py
│   ├── service.py
│   └── schemas.py
├── users/              # Регистрация, профиль пользователя
│   ├── router.py
│   ├── service.py
│   ├── models.py
│   └── schemas.py
├── core/               # Настройки, конфиг, подключение к БД и Redis
├── main.py             # Точка входа, подключение роутеров
migrations/             # Alembic-миграции
tests/
├── unit/               # Юнит-тесты (сервисы, утилиты)
├── functional/         # Функциональные тесты (роутеры)
└── integration/        # Интеграционные тесты (БД, Redis)
Dockerfile
docker-compose.yml
pyproject.toml
.env.example
```

---

## 🚀 Быстрый старт

### Вариант 1 — Docker (рекомендуется)

```bash
# 1. Клонировать репозиторий
git clone <URL_репозитория>
cd auth-service

# 2. Настроить окружение
cp .env.example .env

# 3. Запустить
docker compose up -d --build
```

### Вариант 2 — Локально

```bash
# 1. Установить зависимости
uv sync

# 2. Настроить окружение
cp .env.example .env

# 3. Запустить
uv run uvicorn src.main:app --reload
```

После запуска:

| Сервис | Адрес |
|---|---|
| REST API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Redoc | http://localhost:8000/redoc |

---

## ⚙️ Переменные окружения

Скопируйте `.env.example` → `.env` и заполните:

| Переменная | Пример | Описание |
|---|---|---|
| `DB_HOST` | `localhost` | Хост PostgreSQL |
| `DB_NAME` | `authdb` | Имя базы данных |
| `DB_USER` | `postgres` | Пользователь БД |
| `DB_PASSWORD` | `password` | Пароль БД |
| `REDIS_URL` | `redis://localhost:6379` | Подключение к Redis |
| `SECRET_KEY` | `supersecretkey` | Секрет для JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Время жизни access-токена (мин) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Время жизни refresh-токена (дни) |

---

## 🗃 Миграции

```bash
# В Docker
docker compose exec app uv run alembic upgrade head

# Локально
uv run alembic upgrade head
```

---

## 🧪 Тестирование

```bash
# Локально
pytest

# В Docker
docker compose exec app uv run pytest -s

# С отчётом о покрытии
pytest --cov=src --cov-report=term-missing
```

Тесты разбиты на три уровня и служат образцом для тестирования новых модулей.

---

## 🔧 Использование как шаблон

1. Нажмите **Use this template** на GitHub или клонируйте репозиторий
2. Переименуйте проект в `pyproject.toml` (`name`, `description`)
3. Обновите `.env` под своё окружение
4. Добавляйте новые фичи в `src/` по образцу `users/` или `auth/`
5. Подключите новые роутеры в `main.py`
6. При изменении моделей — создайте новую миграцию: `alembic revision --autogenerate -m "your message"`
