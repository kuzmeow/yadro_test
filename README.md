# Notification Service

## 📋 Оглавление

- [Подготовка к запуску проекта](#подготовка-к-запуску-проекта)
    - [Конфигурации](#конфигурации)
    - [Используя make](#используя-make)
    - [Вручную](#вручную)
- [Запуск проекта](#запуск-проекта)
    - [Локальный запуск бэка без контейнеров](#локальный-запуск-бэка-без-контейнеров)
    - [Локальный запуск бэка из контейнера](#локальный-запуск-бэка-из-контейнера)
- [Запуск тестов](#запуск-тестов)
- [Примеры curl-запросов](#примеры-curl-запросов)
- [Структура проекта](#структура-проекта)
    - [Технологии](#технологии)
    - [Архитектура](#архитектура)
    - [Структура файлов](#структура-файлов)
- [Обработка ошибок](#обработка-ошибок)
    - [Принцип работы](#принцип-работы)
    - [Формат ответа](#формат-ответа-при-ошибке)
    - [Таблица кодов ошибок](#таблица-кодов-ошибок)
    - [Детали ошибок](#детали-ошибок)
    - [Логирование](#логирование-ошибок)

---

## Подготовка к запуску проекта

### Конфигурации

1. Создать файл `.env` из файла `.env.example`

### Используя make

Достаточно выполнить команду:

```bash
make install_dev
```

Будет инициализировано виртуальное окружение, установлены пакеты и подключен pre-commit

### Вручную

1. Инициализация проекта:
    ```bash
	uv sync --all-extras
    ```
2. Подключение pre-commit:
    ```bash
    uv run pre-commit install
    ```

---

## Запуск проекта

### Локальный запуск бэка без контейнеров

#### Используя make

- Если контейнеры БД и других сервисов не подняты:
   ```bash
   make run_all
   make run_taskiq
   ```
- Если контейнеры подняты и надо только запустить проект:
   ```bash
   make run
   make run taskiq
   ```

#### Вручную

1. Поднять контейнеры с необходимым:
   ```bash
   docker compose up postgres redis -d
   ```
2. Запустить проект:
   ```bash
   uv run app
   uv run taskiq worker notification_service.infra.taskiq.taskiq_broker:broker notification_service.infra.taskiq.tasks
   ```

Важно: Если бд поднимаются в докере, а бэк в терминале, то в .env
для параметров DATABASE_URL и REDIS_URL нужно в качестве хоста указывать localhost

### Локальный запуск бэка из контейнера

#### Используя make

- Если контейнеры БД и других сервисов не подняты:
   ```bash
   make run_docker_all
   ```
- Если контейнеры БД подняты и надо только запустить проект:
   ```bash
   make run_docker_back
   ```

#### Вручную

- Если контейнеры БД и других сервисов не подняты:
   ```bash
   docker compose up --build
   ```

- Если контейнеры БД подняты и надо только запустить проект:
   ```bash
	docker compose up notification-service taskiq --build
   ```

## Запуск тестов

### Используя make

Для linux

```bash
make test
```

Для windows

```bash
make shell_test
```

### Вручную

Для linux

```bash
export ENV_FOR_DYNACONF=test; uv run pytest
```

Для windows

```bash
@set ENV_FOR_DYNACONF=test && uv run pytest
```

## Примеры curl-запросов

### Успешные запросы постановки уведомления в очередь

```bash
curl -X POST http://localhost:8000/api/v1/notifications/ \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "recipient": "user@example.com",
    "subject": "Добро пожаловать",
    "message": "Привет! Спасибо за регистрацию.",
    "channel_data": {
      "reply_to": "support@domain.com",
      "priority": "high"
    }
  }'
```

```bash
curl -X POST http://localhost:8000/api/v1/notifications/ \
  -H "Content-Type: application/json" \
  -d '{
    "type": "sms",
    "recipient": "+79991234567",
    "message": "Ваш код подтверждения: 4821",
    "channel_data": {
      "sender_id": "MyApp",
      "flash": false
    }
  }'
```

```bash
curl -X POST http://localhost:8000/api/v1/notifications/ \
  -H "Content-Type: application/json" \
  -d '{
    "type": "telegram",
    "recipient": "@username",
    "message": "<b>Важное</b> уведомление от бота",
    "channel_data": {
      "parse_mode": "HTML",
      "disable_notification": true
    }
  }'
```

#### Ожидаемый ответ

```json
{
  "uid": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "error": null
}
```

### Запросы для получения уведомлений с фильтрами и пагинацией

#### Без параметров (возвращает до 100 записей, значение можно настроить в .env)

```bash
curl -X GET http://localhost:8000/api/v1/notifications/ \
  -H "Accept: application/json"
```

#### С фильтром по статусу

```bash
curl -X GET "http://localhost:8000/api/v1/notifications/?status=failed" \
  -H "Accept: application/json"
```

#### С пагинацией

```bash
curl -X GET "http://localhost:8000/api/v1/notifications/?limit=5&offset=5" \
  -H "Accept: application/json"
```

#### Ожидаемый ответ

```json
[
  {
    "uid": "...",
    "status": "queued",
    "error": null
  },
  {
    "uid": "...",
    "status": "sent",
    "error": null
  },
  {
    "uid": "...",
    "status": "failed",
    "error": "{'message': 'Simulated error'}"
  }
]
```

---

# Структура проекта

Микросервис управления уведомлениями с асинхронной обработкой через TaskIQ.
Построен по принципам Clean Architecture и Domain-Driven Design (DDD).

## Технологии

| Компонент            | Технология              |
|----------------------|-------------------------|
| **Web Framework**    | Flask                   |
| **Task Queue**       | TaskIQ + Redis          |
| **Database**         | PostgreSQL 17.5         |
| **ORM**              | SQLAlchemy 2.0 (Async)  |
| **Migrations**       | Alembic                 |
| **DI**               | Dishka                  |
| **Validation**       | Pydantic                |
| **Package Manager**  | uv                      |
| **Containerization** | Docker + Docker Compose |

## Архитектура

Проект следует принципам **Clean Architecture** с четким разделением на слои:

```
┌─────────────────────────────────────┐
│     Presentation Layer              │
│  (Routes, Schemas, Exceptions)      │
├─────────────────────────────────────┤
│     Application Layer               │
│ (Use Cases, Services, DI Providers) │
├─────────────────────────────────────┤
│       Domain Layer                  │
│  (Entities, Value Objects,          │
│        Protocols)                   │
├─────────────────────────────────────┤
│    Infrastructure Layer             │
│   (DB, Brokers, Tasks, Loggers)     │
└─────────────────────────────────────┘
```

### Зависимости между слоями:

- **Presentation → Application** (вызывает Use Cases)
- **Application → Domain** (использует Entities и Protocols)
- **Infrastructure → Domain** (реализует Protocols)
- **Domain** ← не зависит ни от чего

## Структура файлов

```
notification-service/
│
├── src/notification_service/          # Исходный код приложения
│   │
│   ├── application/                   # Слой приложения (бизнес-правила + оркестрация)
│   │   ├── di/                        # Dependency Injection (Dishka)
│   │   │   ├── providers/             # Провайдеры зависимостей
│   │   │   │   ├── infrastructure_provider.py  # БД, Redis, брокеры
│   │   │   │   ├── notification_provider.py    # Сервисы уведомлений
│   │   │   │   └── settings_provider.py        # Конфигурация
│   │   │   └── container.py           # Сборка DI-контейнера
│   │   ├── services/                  # Бизнес-сервисы
│   │   │   └── notification_service.py
│   │   ├── use_cases/                 # Use Cases (команды/запросы)
│   │   │   └── notification/
│   │   │       └── enqueue_notification_use_case.py
│   │   └── config.py                  # Настройки приложения
│   │
│   ├── domain/                        # Доменный слой (чистая бизнес-логика)
│   │   ├── common/                    # Общие доменные компоненты
│   │   │   ├── entities/              # Базовые сущности
│   │   │   ├── enums/                 # Перечисления
│   │   │   ├── value_objects/         # Value Objects
│   │   │   ├── exceptions/            # Базовые исключения
│   │   │   └── protocols/             # Интерфейсы (порты)
│   │   │       └── logger_factory_protocol.py
│   │   └── notification/              # Домен уведомлений
│   │       ├── entities/              # Доменные сущности
│   │       │   ├── dto/               # Data Transfer Objects
│   │       │   ├── enums/             # Статусы, типы уведомлений
│   │       │   ├── value_objects/     # ChannelData, Recipient и др.
│   │       │   └── notification_entity.py
│   │       ├── exceptions/            # Доменные исключения
│   │       │   └── notification_exceptions.py
│   │       └── protocols/             # Интерфейсы репозиториев/сервисов
│   │           ├── notification_db_repo_protocol.py
│   │           ├── notification_service_protocol.py
│   │           └── notification_tasks_protocol.py
│   │
│   ├── infra/                         # Инфраструктурный слой (адаптеры)
│   │   ├── broker/                    # Redis брокер
│   │   │   └── adapters/
│   │   │       └── redis_adapter.py
│   │   ├── db/                        # PostgreSQL
│   │   │   ├── adapters/
│   │   │   │   └── postgres_adapter.py
│   │   │   ├── alembic/               # Миграции БД
│   │   │   │   ├── versions/          # Файлы миграций
│   │   │   │   ├── env.py             # Конфигурация Alembic
│   │   │   │   └── script.py.mako     # Шаблон генерации миграций
│   │   │   ├── mappers/               # ORM ↔ Domain мапперы
│   │   │   │   └── notification/
│   │   │   │       └── notification_mapper.py
│   │   │   ├── mixins/                # SQLAlchemy mixins
│   │   │   │   ├── id_mixins.py
│   │   │   │   └── timestamp_mixins.py
│   │   │   ├── models/                # ORM модели
│   │   │   │   ├── base/
│   │   │   │   │   └── base_model.py
│   │   │   │   └── notification/
│   │   │   │       └── notification_model.py
│   │   │   └── repositories/          # Реализации репозиториев
│   │   │       └── notification/
│   │   │           └── notification_db_repository.py
│   │   ├── logger/                    # Логирование
│   │   │   └── project_logger.py
│   │   └── taskiq/                    # TaskIQ задачи и адаптеры
│   │       ├── adapters/
│   │       │   └── taskiq_user_adapter.py
│   │       ├── tasks/
│   │       │   └── notification_tasks.py
│   │       ├── background_loop_manager.py   # Фоновый event loop для post-commit задач
│   │       ├── post_commit_queue.py         # Очередь задач после коммита
│   │       └── taskiq_broker.py             # Конфигурация брокера
│   │
│   └── presentation/                  # Слой представления (API)
│       ├── core/
│       │   └── exception_handler.py   # Глобальная обработка ошибок
│       └── routes/
│           └── notification/
│               ├── notification_mappers.py   # Domain → Schema мапперы
│               ├── notification_routes.py    # Flask routes (эндпоинты)
│               └── notification_schemas.py   # Pydantic схемы (валидация)
│
├── tests/                             # Тесты
│   ├── common/                        # Общие фикстуры и утилиты
│   │   ├── db/
│   │   │   └── db_fixtures.py         # Фикстуры для работы с БД
│   │   ├── factories/                 # Фабрики тестовых данных
│   │   │   ├── adapters.py
│   │   │   ├── repositories.py
│   │   │   └── services.py
│   │   ├── samples/                   # Примеры данных для тестов
│   │   │   └── notification_samples.py
│   │   └── my_mocker.py               # Утилиты для мокирования
│   ├── integration/                   # Интеграционные тесты
│   │   └── infra/
│   │       └── db/
│   │           └── repositories/
│   │               └── notification/
│   │                   └── test_notification_db_repository.py
│   ├── unit/                          # Юнит-тесты
│   │   ├── application/
│   │   │   └── use_cases/
│   │   │       └── notification/
│   │   │           └── test_enqueue_notification_use_case.py
│   │   ├── domain/
│   │   │   └── notification/
│   │   │       └── entities/
│   │   │           ├── test_channel_data.py
│   │   │           └── test_notification_entity.py
│   │   └── presentation/
│   │       └── schemas/
│   │           └── test_notification_schemas.py
│   └── conftest.py                    # Pytest конфигурация и глобальные фикстуры
│
├── docker-compose.yml                 # Основной compose для разработки
├── docker-compose.test.yml            # Compose для тестов (Testcontainers)
├── Dockerfile                         # Образ приложения
├── Makefile                           # Команды для разработки (install, run, test)
├── pyproject.toml                     # Зависимости и метаданные проекта (uv)
├── uv.lock                            # Lock-файл зависимостей (uv)
├── alembic.ini                        # Конфигурация миграций
├── .env.example                       # Шаблон переменных окружения
└── .pre-commit-config.yaml            # Pre-commit хуки (lint, format, type-check)
```

---

## Обработка ошибок

Проект использует единую систему обработки исключений на основе **доменных исключений** и глобальных хендлеров Flask.

### Принцип работы

1. Все бизнес-ошибки наследуются от `DomainException`
2. Каждое исключение имеет:
    - `status_code` — HTTP-статус ответа
    - `prefix` — префикс сервиса (например, `NTF` для уведомлений)
    - `service_code` — уникальный код ошибки внутри сервиса
3. Финальный код ошибки формируется как: **`{prefix}-{service_code}`**
4. Flask-хендлеры перехватывают исключения и возвращают унифицированный JSON-ответ

### Формат ответа при ошибке

```json
{
  "error": {
    "code": "NTF-001",
    "message": "Notification not found",
    "details": {}
  }
}
```

---

## Таблица кодов ошибок

### Ошибки домена уведомлений (`NTF-*`)

| Код       | Статус | Описание                                         | Когда возникает                                                                   |
|-----------|--------|--------------------------------------------------|-----------------------------------------------------------------------------------|
| `NTF-001` | 404    | Notification not found                           | Уведомление с указанным `uid` не найдено в БД                                     |
| `NTF-002` | 400    | Recipient format is invalid for provided type    | Формат получателя не соответствует типу уведомления (например, email для SMS)     |
| `NTF-003` | 400    | Channel Data format is invalid for provided type | Формат `channel_data` не соответствует типу уведомления (например, email для SMS) |
| `NTF-004` | 409    | Notification status conflict                     | Попытка перевести уведомление в невалидный статус (например, `sent` → `queued`)   |
| `NTF-005` | 500    | Notification sending failed                      | Ошибка при отправке уведомления через внешний сервис (SMTP, Telegram API и т.д.)  |

### Системные ошибки (`SYS-*`)

| Код       | Статус | Описание              | Когда возникает                                                        |
|-----------|--------|-----------------------|------------------------------------------------------------------------|
| `SYS-000` | 500    | Internal Server Error | Необработанное исключение в коде приложения                            |
| `SYS-001` | 404    | Resource not found    | Запрошенный URL не соответствует ни одному роуту (Werkzeug `NotFound`) |

### Ошибки валидации (`VAL-*`)

| Код       | Статус | Описание          | Когда возникает                                                                                        |
|-----------|--------|-------------------|--------------------------------------------------------------------------------------------------------|
| `VAL-001` | 422    | Validation failed | Ошибка валидации входных данных через Pydantic (неверный тип, отсутствующее поле, формат email и т.д.) |

---

### Детали ошибок

Некоторые исключения возвращают дополнительную информацию в поле `details`:

#### `NTF-003` — Invalid Channel Data

```json
{
  "error": {
    "code": "NTF-003",
    "message": "Channel Data format is invalid for provided type",
    "details": {
      "expected_type": "email",
      "invalid_keys": [
        "flash",
        "sender_id"
      ]
    }
  }
}
```

#### `NTF-004` — Status Conflict

```json
{
  "error": {
    "code": "NTF-004",
    "message": "Notification status conflict",
    "details": {
      "reason": "Cannot set sent notification status to queued"
    }
  }
}
```

#### `VAL-001` — Validation Failed

```json
{
  "error": {
    "code": "VAL-001",
    "message": "Validation failed",
    "details": {
      "fields": [
        {
          "field": "recipient",
          "reason": "value is not a valid email address"
        },
        {
          "field": "type",
          "reason": "field required"
        }
      ]
    }
  }
}
```

---

### Логирование ошибок

- Все `DomainException` со статусом `500` логируются на уровне `ERROR` через `LoggerFactory`. В `details` у них
  содержится важная информация, которая и логируется. Клиент эти подробности не получает
- Необработанные исключения, не наследуемые от `DomainException` логируются с полным стек-трейсом (`logger.exception`)
- Для отладки в `.env` можно установить `LOG_LEVEL=DEBUG`
