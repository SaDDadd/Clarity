# Clarity — Task Management API

**Clarity** — это серверная часть (бэкенд) для системы управления проектами и задачами.  
Проект построен на **FastAPI** с использованием асинхронной **SQLAlchemy**, **MySQL**, **JWT-аутентификации** и **Alembic** для миграций.

Бэкенд предоставляет RESTful API, которое может использоваться любым фронтендом (веб, мобильное приложение и т.д.).

---

## Содержание

- [Основные возможности](#основные-возможности)
- [Используемые технологии](#используемые-технологии)
- [Архитектура проекта](#архитектура-проекта)
- [Установка и запуск](#установка-и-запуск)
  - [Локальный запуск (без Docker)](#локальный-запуск-без-docker)
  - [Запуск через Docker Compose](#запуск-через-docker-compose)
- [Переменные окружения](#переменные-окружения-файл-env)
- [Миграции базы данных](#миграции-базы-данных)
- [Описание таблиц базы данных](#описание-таблиц-базы-данных)
- [Документация API](#документация-api)
  - [Аутентификация](#аутентификация)
  - [Проекты](#проекты)
  - [Задачи](#задачи)
  - [Приглашения](#приглашения)
  - [Профиль пользователя](#профиль-пользователя)
- [Тестирование](#тестирование)
- [Инструкция для фронтенда](#инструкция-для-фронтенда)
- [Структура проекта](#структура-проекта)

---

## Основные возможности

- Регистрация и аутентификация пользователей (JWT).
- Управление проектами (создание, просмотр, обновление, удаление).
- Ролевая модель: **admin** и **member** в рамках проекта.
- Управление задачами внутри проектов (CRUD, смена статуса).
- Приглашения пользователей в проекты.
- Профиль пользователя (смена имени и email).
- Пагинация для списков (реализована, но не задокументирована — будет добавлена в следующих релизах).
- Полностью асинхронный код.
- Docker-контейнеризация.
- Написанные тесты (pytest + httpx).

---

## Используемые технологии

- **Python 3.10+**
- **FastAPI** — веб-фреймворк
- **SQLAlchemy** (асинхронный) — ORM
- **MySQL** — база данных
- **Alembic** — миграции
- **Pydantic** — валидация данных
- **python-jose** — JWT
- **passlib** — хеширование паролей
- **pytest + httpx** — тестирование
- **Docker / Docker Compose** — контейнеризация

---

## Архитектура проекта

Проект построен по многослойной архитектуре:

- **API слой** (`api/v1/`) — роутеры FastAPI.
- **Слой сервисов** (`services/`) — бизнес-логика.
- **Репозитории** (`repositories/`) — работа с базой данных.
- **Модели** (`models/`) — SQLAlchemy-модели.
- **Схемы** (`schemas/`) — Pydantic-схемы для валидации запросов и ответов.
- **Ядро** (`core/`) — конфигурация, безопасность, зависимости, исключения.

Такая структура обеспечивает **разделение ответственности**, упрощает тестирование и поддержку кода.

---

## Установка и запуск

### Локальный запуск (без Docker)

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/SaDDadd/Clarity.git
   cd Clarity
   ```

2. **Создайте и активируйте виртуальное окружение:**
   ```bash
   python -m venv venv
   source venv/bin/activate   # для Linux/Mac
   # или
   venv\Scripts\activate      # для Windows
   ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Создайте файл `.env`** (см. раздел [Переменные окружения](#переменные-окружения-файл-env)).

5. **Запустите MySQL** (локально или в контейнере) и создайте базу данных.

6. **Примените миграции:**
   ```bash
   alembic upgrade head
   ```

7. **Запустите приложение:**
   ```bash
   uvicorn main:app --reload
   ```
   API будет доступно по адресу `http://localhost:8000`.

---

### Запуск через Docker Compose

Для запуска всего приложения (бэкенд + MySQL) в контейнерах:

1. Убедитесь, что установлены **Docker** и **Docker Compose**.
2. Создайте файл `.env` в корне проекта (как описано в разделе переменных окружения).
3. Соберите и запустите контейнеры:
   ```bash
   docker-compose up --build
   ```
   - Бэкенд будет доступен на `http://localhost:8000`
   - База данных MySQL будет доступна на порту `3307` хоста (внутри контейнера – `3306`).
   - При старте контейнера бэкенда автоматически выполняются миграции (скрипт `entrypoint.sh`).
4. Остановка:
   ```bash
   docker-compose down
   ```

> **Важно:** при использовании Docker переменные окружения загружаются из файла `.env`. Убедитесь, что все необходимые переменные заданы.

---

## Переменные окружения (файл `.env`)

Пример содержимого `.env`:

```env
# База данных
DB_HOST=db                   # для Docker – имя сервиса db; для локального запуска – localhost
DB_PORT=3306                 # порт внутри контейнера; при локальном запуске обычно 3306
DB_USER=root
DB_PASSWORD=your_secure_password
DB_NAME=task_to_do
DB_DRIVER=aiomysql

# JWT
JWT_SECRET_KEY=your_super_secret_key_here   # обязательно задайте надёжный ключ
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (опционально)
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

Все настройки загружаются из класса `Settings` в `core/config.py`.  
Значение `JWT_SECRET_KEY` **обязательно** должно быть задано в `.env`.

Для запуска тестов используется файл `.env.test`:

```env
DB_HOST=db
DB_PORT=3306
DB_USER=root
DB_PASSWORD=2007
DB_NAME=task_to_do_test
JWT_SECRET_KEY=your_very_secret_key_here_32_chars_min
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Он подключается в `core/config.py` через `SettingsTEST`.

---

## Миграции базы данных

Для управления схемой используется **Alembic**.

- **Создать новую миграцию** (после изменения моделей):
  ```bash
  alembic revision --autogenerate -m "описание изменений"
  ```

- **Применить миграции:**
  ```bash
  alembic upgrade head
  ```

- **Откатиться на предыдущую версию:**
  ```bash
  alembic downgrade -1
  ```

> **Важно:** перед созданием миграции убедитесь, что ваши модели импортированы в `env.py`, чтобы Alembic мог их обнаружить.

---

## Описание таблиц базы данных

Схема базы данных состоит из пяти таблиц, описанных ниже.

### Таблица `users` (пользователи)

| Поле            | Тип            | Ограничения                         | Описание                   |
|-----------------|----------------|-------------------------------------|----------------------------|
| `user_id`       | `int`          | PRIMARY KEY, AUTO_INCREMENT         | Уникальный идентификатор   |
| `username`      | `varchar(50)`  | NOT NULL, UNIQUE                    | Имя пользователя           |
| `email`         | `varchar(100)` | NOT NULL, UNIQUE                    | Электронная почта          |
| `password_hash` | `varchar(255)` | NOT NULL                            | Хеш пароля                 |
| `created_date`  | `timestamp`    | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Дата регистрации           |

### Таблица `projects` (проекты)

| Поле                  | Тип             | Ограничения                 | Описание                |
|-----------------------|-----------------|-----------------------------|-------------------------|
| `project_id`          | `int`           | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `project_name`        | `varchar(100)`  | NOT NULL                    | Название проекта        |
| `project_description` | `text`          | YES                         | Описание проекта         |
| `admin_id`            | `int`           | NOT NULL, FOREIGN KEY       | ID создателя (админа)   |

### Таблица `project_members` (участники проектов)

| Поле         | Тип        | Ограничения                         | Описание                        |
|--------------|------------|-------------------------------------|---------------------------------|
| `project_id` | `int`      | NOT NULL, FOREIGN KEY               | ID проекта                      |
| `user_id`    | `int`      | NOT NULL, FOREIGN KEY               | ID пользователя                 |
| `role_project`| `enum`     | NOT NULL, DEFAULT 'member'          | Роль (`admin` или `member`)     |
| `joined_date`| `timestamp`| NOT NULL, DEFAULT CURRENT_TIMESTAMP | Дата присоединения              |

### Таблица `tasks` (задачи)

| Поле                | Тип                                      | Ограничения                         | Описание                          |
|---------------------|------------------------------------------|-------------------------------------|-----------------------------------|
| `task_id`           | `int`                                    | PRIMARY KEY, AUTO_INCREMENT         | Уникальный идентификатор          |
| `title`             | `varchar(150)`                           | NOT NULL                            | Название задачи                   |
| `task_description`  | `text`                                   | YES                                 | Описание задачи                   |
| `task_status`       | `enum('pending','in_progress','completed')` | YES, DEFAULT 'pending'            | Статус задачи                     |
| `project_id`        | `int`                                    | NOT NULL, FOREIGN KEY               | ID проекта                        |
| `assigned_to`       | `int`                                    | YES, FOREIGN KEY                    | ID исполнителя                    |
| `deadline`          | `date`                                   | YES                                 | Срок выполнения                   |
| `created_date`      | `timestamp`                              | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Дата создания                     |

### Таблица `project_invitations` (приглашения)

| Поле            | Тип                                      | Ограничения                         | Описание                          |
|-----------------|------------------------------------------|-------------------------------------|-----------------------------------|
| `invitation_id` | `int`                                    | PRIMARY KEY, AUTO_INCREMENT         | Уникальный идентификатор          |
| `project_id`    | `int`                                    | NOT NULL, FOREIGN KEY               | ID проекта                        |
| `inviter_id`    | `int`                                    | NOT NULL, FOREIGN KEY               | ID пригласившего                  |
| `invitee_id`    | `int`                                    | NOT NULL, FOREIGN KEY               | ID приглашённого                  |
| `status_invited`| `enum('pending','accepted','declined')`  | YES, DEFAULT 'pending'              | Статус приглашения                |
| `created_date`  | `timestamp`                              | YES, DEFAULT CURRENT_TIMESTAMP      | Дата создания                     |
| `update_date`   | `timestamp`                              | YES, DEFAULT CURRENT_TIMESTAMP      | Дата последнего обновления        |
| `message`       | `text`                                   | YES                                 | Сообщение к приглашению           |

---

## Документация API

**Базовый URL:** `http://localhost:8000/api/v1`

Все эндпоинты, кроме регистрации и логина, требуют **JWT-аутентификации**.  
Токен передаётся в заголовке:
```
Authorization: Bearer <access_token>
```

---

### Аутентификация

| Метод | Эндпоинт           | Описание                          | Требует аутентификации |
|-------|--------------------|-----------------------------------|------------------------|
| POST  | `/auth/register`   | Регистрация нового пользователя   | ❌                     |
| POST  | `/auth/login`      | Вход в систему (получение токена)| ❌                     |
| GET   | `/auth/me`         | Получить информацию о текущем пользователе | ✅          |

#### Регистрация

**Запрос:**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123"
}
```

**Успешный ответ (201 Created):**
```json
{
    "message": "Пользователь создан"
}
```

**Ошибки:**
- `409 Conflict` — имя пользователя или email уже заняты.
- `422 Unprocessable Entity` — пароль короче 8 символов.

---

#### Логин

**Запрос:**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "username_or_email": "john_doe",
    "password": "securepassword123"
}
```

**Успешный ответ (200 OK):**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```

**Ошибки:**
- `401 Unauthorized` — неверные учётные данные.
- `422 Unprocessable Entity` — пустые поля.

---

#### Получение информации о текущем пользователе

**Запрос:**
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

**Успешный ответ (200 OK):**
```json
{
    "user_id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_date": "2026-08-20T10:00:00"
}
```

---

### Проекты

| Метод   | Эндпоинт                              | Описание                                           | Требует аутентификации | Роль      |
|---------|---------------------------------------|----------------------------------------------------|------------------------|-----------|
| POST    | `/projects`                           | Создать проект                                     | ✅                      | -         |
| GET     | `/projects`                           | Список проектов, где пользователь — админ          | ✅                      | -         |
| GET     | `/projects/all`                       | Список всех проектов, где пользователь участвует   | ✅                      | -         |
| GET     | `/projects/{project_id}`              | Получить информацию о проекте                      | ✅                      | member/admin |
| PUT     | `/projects/{project_id}`              | Обновить проект                                    | ✅                      | admin     |
| DELETE  | `/projects/{project_id}`              | Удалить проект                                     | ✅                      | admin     |
| POST    | `/projects/{project_id}/members`      | Добавить участника в проект                        | ✅                      | admin     |
| DELETE  | `/projects/{project_id}/members`      | Удалить участника из проекта                       | ✅                      | admin     |
| PATCH   | `/projects/{project_id}/members/{user_id}/role` | Изменить роль участника | ✅                      | admin     |

---

#### Создание проекта

**Запрос:**
```http
POST /api/v1/projects
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "project_name": "Новый проект",
    "project_description": "Описание проекта"
}
```

**Успешный ответ (201 Created):**
```json
{
    "project_id": 1,
    "project_name": "Новый проект",
    "project_description": "Описание проекта",
    "admin_id": 1
}
```

---

#### Получение списка проектов (где пользователь — админ)

**Запрос:**
```http
GET /api/v1/projects
Authorization: Bearer <access_token>
```

**Успешный ответ (200 OK):**
```json
[
    {
        "project_id": 1,
        "project_name": "Новый проект",
        "project_description": "Описание проекта",
        "admin_id": 1
    }
]
```

---

#### Получение списка всех проектов пользователя (админ + участник)

**Запрос:**
```http
GET /api/v1/projects/all
Authorization: Bearer <access_token>
```

**Успешный ответ (200 OK):**
```json
[
    {
        "project_id": 1,
        "project_name": "Новый проект",
        "project_description": "Описание проекта",
        "role": "admin"
    },
    {
        "project_id": 2,
        "project_name": "Чужой проект",
        "project_description": "Описание",
        "role": "member"
    }
]
```

---

#### Получение информации о проекте

**Запрос:**
```http
GET /api/v1/projects/1
Authorization: Bearer <access_token>
```

**Успешный ответ (200 OK):**
```json
{
    "project_id": 1,
    "project_name": "Новый проект",
    "project_description": "Описание проекта",
    "admin_id": 1,
    "members": [
        {
            "user_id": 1,
            "username": "john_doe",
            "role": "admin"
        },
        {
            "user_id": 2,
            "username": "jane_doe",
            "role": "member"
        }
    ]
}
```

**Ошибки:**
- `404 Not Found` — проект не найден.
- `403 Forbidden` — пользователь не является участником проекта.

---

#### Обновление проекта

**Запрос:**
```http
PUT /api/v1/projects/1
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "project_name": "Обновлённое название",
    "project_description": "Новое описание"
}
```

**Успешный ответ (200 OK):**
```json
{
    "message": "Проект обновлен!"
}
```

Если данные не изменились:
```json
{
    "message": "Ничего не изменилось!"
}
```

**Ошибки:**
- `403 Forbidden` — пользователь не админ проекта.
- `404 Not Found` — проект не найден.

---

#### Удаление проекта

**Запрос:**
```http
DELETE /api/v1/projects/1
Authorization: Bearer <access_token>
```

**Успешный ответ (200 OK):**
```json
{
    "message": "Проект успешно удален!"
}
```

**Ошибки:**
- `403 Forbidden` — пользователь не админ проекта.
- `404 Not Found` — проект не найден.

---

#### Добавление участника в проект

**Запрос:**
```http
POST /api/v1/projects/1/members
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "user_id": 2
}
```

**Успешный ответ (201 Created):**
```json
{
    "message": "Пользователь добавлен в проект!"
}
```

**Ошибки:**
- `400 Bad Request` — попытка добавить самого себя.
- `403 Forbidden` — пользователь не админ проекта.
- `404 Not Found` — пользователь не найден.
- `409 Conflict` — пользователь уже состоит в проекте.

---

#### Удаление участника из проекта

**Запрос:**
```http
DELETE /api/v1/projects/1/members
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "user_id": 2
}
```

**Успешный ответ (200 OK):**
```json
{
    "message": "Пользователь удален из проекта!"
}
```

**Ошибки:**
- `400 Bad Request` — попытка удалить самого себя (единственного админа).
- `403 Forbidden` — пользователь не админ проекта.
- `409 Conflict` — пользователь не состоит в проекте.

---

#### Изменение роли участника

**Запрос:**
```http
PATCH /api/v1/projects/1/members/2/role?role=admin
Authorization: Bearer <access_token>
```

**Успешный ответ (200 OK):**
```json
{
    "message": "Роль обновлена"
}
```

**Ошибки:**
- `400 Bad Request` — попытка понизить единственного админа.
- `403 Forbidden` — пользователь не админ проекта.

---

### Задачи

| Метод   | Эндпоинт                                     | Описание                                      | Требует аутентификации | Роль      |
|---------|----------------------------------------------|-----------------------------------------------|------------------------|-----------|
| GET     | `/tasks`                                     | Получить задачи, назначенные текущему пользователю | ✅                  | -         |
| GET     | `/projects/{project_id}/tasks`               | Получить все задачи проекта                   | ✅                      | member/admin |
| GET     | `/projects/{project_id}/tasks/{task_id}`     | Получить детали задачи                        | ✅                      | member/admin |
| POST    | `/projects/{project_id}/tasks`               | Создать задачу в проекте                      | ✅                      | member/admin |
| PUT     | `/projects/{project_id}/tasks/{task_id}`     | Обновить задачу                               | ✅                      | member/admin |
| PATCH   | `/projects/{project_id}/tasks/{task_id}/status` | Изменить статус задачи                     | ✅                      | member/admin |
| DELETE  | `/projects/{project_id}/tasks/{task_id}`     | Удалить задачу                                | ✅                      | admin     |

---

#### Создание задачи

**Запрос:**
```http
POST /api/v1/projects/1/tasks
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "title": "Написать документацию",
    "task_description": "Описание задачи",
    "task_status": "pending",        // или "in_progress", "completed"
    "assigned_to": 2,                // ID пользователя (опционально)
    "deadline": "2026-09-01"         // в формате YYYY-MM-DD
}
```

**Успешный ответ (201 Created):**
```json
{
    "task_id": 1,
    "title": "Написать документацию",
    "task_description": "Описание задачи",
    "task_status": "pending",
    "project_id": 1,
    "assigned_to": 2,
    "deadline": "2026-09-01",
    "created_date": "2026-08-20T10:00:00"
}
```

---

#### Получение всех задач проекта

**Запрос:**
```http
GET /api/v1/projects/1/tasks
Authorization: Bearer <access_token>
```

**Успешный ответ (200 OK):**
```json
[
    {
        "task_id": 1,
        "title": "Написать документацию",
        "task_status": "pending",
        "assigned_to": 2,
        "deadline": "2026-09-01"
    }
]
```

---

#### Получение деталей задачи

**Запрос:**
```http
GET /api/v1/projects/1/tasks/1
Authorization: Bearer <access_token>
```

**Успешный ответ (200 OK):**
```json
{
    "task_id": 1,
    "title": "Написать документацию",
    "task_description": "Описание задачи",
    "task_status": "pending",
    "project_id": 1,
    "assigned_to": 2,
    "deadline": "2026-09-01",
    "created_date": "2026-08-20T10:00:00"
}
```

---

#### Обновление задачи

**Запрос:**
```http
PUT /api/v1/projects/1/tasks/1
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "title": "Обновлённый заголовок",
    "task_description": "Новое описание",
    "task_status": "in_progress",
    "assigned_to": 3,
    "deadline": "2026-10-01"
}
```

**Успешный ответ (200 OK):**
```json
{
    "message": "Задача обновлена"
}
```

---

#### Изменение статуса задачи

**Запрос:**
```http
PATCH /api/v1/projects/1/tasks/1/status
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "task_status": "completed"
}
```

**Успешный ответ (200 OK):**
```json
{
    "message": "Статус обновлен!"
}
```

---

#### Удаление задачи

**Запрос:**
```http
DELETE /api/v1/projects/1/tasks/1
Authorization: Bearer <access_token>
```

**Успешный ответ (200 OK):**
```json
{
    "message": "Задача успешно удалена"
}
```

**Ошибки:**
- `403 Forbidden` — пользователь не админ проекта.

---

#### Получение задач, назначенных текущему пользователю

**Запрос:**
```http
GET /api/v1/tasks
Authorization: Bearer <access_token>
```

**Успешный ответ (200 OK):**
```json
[
    {
        "task_id": 1,
        "title": "Написать документацию",
        "task_status": "pending",
        "project_id": 1,
        "deadline": "2026-09-01"
    }
]
```

---

### Приглашения

| Метод   | Эндпоинт                                   | Описание                                      | Требует аутентификации | Роль      |
|---------|--------------------------------------------|-----------------------------------------------|------------------------|-----------|
| POST    | `/projects/{project_id}/invitations`       | Отправить приглашение в проект                | ✅                      | admin     |
| GET     | `/invitations`                             | Список входящих приглашений для пользователя  | ✅                      | -         |
| GET     | `/invitations/project/{project_id}`        | Список приглашений проекта                    | ✅                      | admin     |
| PATCH   | `/invitations/{invitation_id}`             | Принять/отклонить приглашение                 | ✅                      | invitee   |
| DELETE  | `/invitations/{invitation_id}`             | Отменить приглашение                          | ✅                      | admin/inviter |

---

#### Отправка приглашения

**Запрос:**
```http
POST /api/v1/projects/1/invitations
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "user_id": 3,
    "message": "Присоединяйся к нашему проекту!"
}
```

**Успешный ответ (200 OK):**
```json
{
    "invitation_id": 1,
    "project_id": 1,
    "inviter_id": 1,
    "invitee_id": 3,
    "status_invited": "pending",
    "created_date": "2026-08-20T10:00:00",
    "update_date": "2026-08-20T10:00:00",
    "message": "Присоединяйся к нашему проекту!"
}
```

---

#### Получение списка приглашений для пользователя

**Запрос:**
```http
GET /api/v1/invitations
Authorization: Bearer <access_token>
```

**Успешный ответ (200 OK):**
```json
[
    {
        "invitation_id": 1,
        "project_id": 1,
        "inviter_id": 1,
        "invitee_id": 3,
        "status_invited": "pending",
        "created_date": "2026-08-07T20:13:03",
        "update_date": "2026-08-07T20:13:03",
        "message": "Присоединяйся к нашему проекту!"
    }
]
```

---

#### Получение списка приглашений проекта

**Запрос:**
```http
GET /api/v1/invitations/project/1
Authorization: Bearer <access_token>
```

**Успешный ответ (200 OK):**
```json
[
    {
        "invitation_id": 1,
        "invitee_id": 3,
        "status_invited": "pending",
        "created_date": "2026-08-07T20:13:03"
    }
]
```

---

#### Ответ на приглашение

**Запрос:**
```http
PATCH /api/v1/invitations/1
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "action": "accepted"   // или "declined"
}
```

**Успешный ответ (200 OK):**
```json
{
    "message": "Приглашение accepted"
}
```

При успешном принятии пользователь автоматически добавляется в проект как участник.

---

#### Отмена приглашения

**Запрос:**
```http
DELETE /api/v1/invitations/1
Authorization: Bearer <access_token>
```

**Успешный ответ (200 OK):**
```json
{
    "message": "Приглашение отменено"
}
```

---

### Профиль пользователя

| Метод | Эндпоинт           | Описание                      | Требует аутентификации |
|-------|--------------------|-------------------------------|------------------------|
| PUT   | `/profile/username`| Обновить имя пользователя     | ✅                      |
| PUT   | `/profile/email`   | Обновить email пользователя   | ✅                      |

---

#### Обновление имени

**Запрос:**
```http
PUT /api/v1/profile/username
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "username": "new_username"
}
```

**Успешный ответ (200 OK):**
```json
{
    "message": "Имя пользователя обновлено!"
}
```

---

#### Обновление email

**Запрос:**
```http
PUT /api/v1/profile/email
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "email": "new_email@example.com"
}
```

**Успешный ответ (200 OK):**
```json
{
    "message": "Email пользователя обновлено!"
}
```

---

## Тестирование

Для тестирования API используется **pytest** с асинхронной поддержкой и **httpx**.

### Структура тестов

```
tests/
├── conftest.py                 # Фикстуры и настройка pytest
├── test_api/
│   ├── test_auth.py            # Тесты аутентификации
│   ├── test_projects.py        # Тесты проектов
│   ├── test_tasks.py           # Тесты задач
│   ├── test_invitations.py     # Тесты приглашений
│   └── test_profile.py         # Тесты профиля
├── test_repositories/          # Тесты репозиториев (в разработке)
└── test_services/              # Тесты сервисов (в разработке)
```

### Запуск тестов

1. Убедитесь, что создан файл `.env.test` с настройками для тестовой базы данных.
2. Запустите тесты:
   ```bash
   pytest -v
   ```

### Описание основных фикстур (`conftest.py`)

| Фикстура | Описание |
|----------|----------|
| `engine` | Создаёт асинхронный движок SQLAlchemy, применяет миграции перед тестами и откатывает их после. |
| `db_session` | Создаёт новую сессию базы данных для каждого теста. |
| `async_client` | Предоставляет асинхронный HTTP-клиент для тестирования эндпоинтов без запуска сервера. |
| `create_test_user` | Создаёт тестового пользователя с заданным паролем. |
| `test_users` | Создаёт трёх тестовых пользователей: `admin`, `member`, `outsider`. |
| `auth_headers` | Возвращает заголовки с JWT-токеном для пользователя `admin`. |
| `member_auth_headers` | Возвращает заголовки с JWT-токеном для пользователя `member`. |
| `test_project` | Создаёт тестовый проект с пользователем `admin` в роли администратора. |
| `test_project_with_member` | Создаёт тестовый проект и добавляет в него пользователя `member`. |
| `test_task` | Создаёт тестовую задачу в проекте. |

### Примеры тестов

#### Тесты аутентификации (`test_auth.py`)

- `test_register_success` — успешная регистрация.
- `test_register_duplicate_username` — попытка регистрации с существующим именем.
- `test_register_duplicate_email` — попытка регистрации с существующим email.
- `test_login_success_username` — успешный вход по имени пользователя.
- `test_login_success_email` — успешный вход по email.
- `test_login_wrong_password` — попытка входа с неверным паролем.
- `test_login_user_not_found` — попытка входа с несуществующим пользователем.
- `test_login_empty_fields` — попытка входа с пустыми полями.
- `test_short_password` — попытка регистрации с коротким паролем.

#### Тесты проектов (`test_projects.py`)

- `test_successful_project_creation` — успешное создание проекта.
- `test_attempt_create_project_without_authorization` — создание проекта без токена.
- `test_attempt_create_project_with_incorrect_data` — создание проекта с некорректными данными.
- `test_authorized_admin_projects_returned` — получение списка проектов, где пользователь — админ.
- `test_attempt_get_non_existent_project` — попытка получить несуществующий проект.
- `test_attempt_get_project_that_user_not_part` — попытка получить проект, в котором пользователь не состоит.
- `test_authorized_user_projects_returned` — получение всех проектов пользователя.
- `test_getting_project_lets_project_participant_see_details` — участник проекта получает его детали.
- `test_admin_update_project` — админ обновляет проект.
- `test_regular_participant_not_update_project` — обычный участник не может обновить проект.
- `test_admin_delete_project` — админ удаляет проект.
- `test_regular_participant_not_delete_project` — обычный участник не может удалить проект.
- `test_admin_add_existing_user` — админ добавляет пользователя в проект.
- `test_adding_yourself` — попытка добавить самого себя.
- `test_admin_not_add_user_already_in_project` — попытка добавить уже существующего участника.
- `test_admin_delete_anyone` — админ удаляет участника.
- `test_regular_member_not_delete_anyone` — обычный участник не может удалить другого.
- `test_admin_raise_or_lower_role` — админ повышает/понижает роль.
- `test_not_demote_only_admin` — попытка понизить единственного админа.
- `test_empty_projects_list_for_new_user` — новый пользователь получает пустой список.
- `test_regular_member_add_user_to_project` — обычный участник не может добавить пользователя.
- `test_admin_add_non_existent_user` — попытка добавить несуществующего пользователя.
- `test_admin_delete_user_not_in_project` — попытка удалить пользователя, не состоящего в проекте.
- `test_member_projects_list` — участник видит проекты, в которых состоит.
- `test_regular_member_change_role` — обычный участник не может изменить роль.
- `test_add_user_to_non_existent_project` — попытка добавить пользователя в несуществующий проект.
- `test_update_project_with_no_changes` — обновление проекта без изменений.
- `test_update_project_user_not_member` — попытка обновить проект пользователем, не состоящим в нём.
- `test_admin_delete_self_from_project` — попытка админа удалить самого себя (запрещено).

---

## Инструкция для фронтенда

### 1. Базовый URL

Все запросы отправляются на `http://localhost:8000/api/v1` (в продакшене – ваш домен).

### 2. Аутентификация

- После успешного логина сервер возвращает `access_token`.
- Этот токен необходимо отправлять с каждым защищённым запросом в заголовке:
  ```
  Authorization: Bearer <access_token>
  ```
- Токен действителен **30 минут** (настраивается в `.env`). По истечении срока пользователь должен повторно войти.

### 3. Форматы данных

- Все даты передаются в формате ISO 8601:
  - `YYYY-MM-DD` для дат без времени.
  - `YYYY-MM-DDTHH:MM:SS` для datetime.
- Enum-поля (статусы задач, роли) передаются строками:
  - `task_status`: `"pending"`, `"in_progress"`, `"completed"`
  - `role_project` (в запросах/ответах): `"admin"`, `"member"`
  - `status_invited`: `"pending"`, `"accepted"`, `"declined"`

### 4. Обработка ошибок

Все ошибки приходят в формате:
```json
{
    "detail": "Текст ошибки"
}
```

HTTP-статусы соответствуют стандартам:
- `200` – успех
- `201` – создано
- `400` – плохой запрос
- `401` – не авторизован
- `403` – доступ запрещён
- `404` – не найдено
- `409` – конфликт (например, дубликат)
- `422` – ошибка валидации

### 5. CORS

Настроен CORS для всех источников (в разработке). Для продакшена укажите конкретные домены через переменную `CORS_ORIGINS` в `.env` (через запятую).

### 6. Пример работы с API на фронтенде (JavaScript)

```javascript
// Логин
const login = async (usernameOrEmail, password) => {
    const res = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username_or_email: usernameOrEmail, password })
    });
    const data = await res.json();
    localStorage.setItem('token', data.access_token);
};

// Запрос защищённого ресурса
const getProjects = async () => {
    const token = localStorage.getItem('token');
    const res = await fetch('http://localhost:8000/api/v1/projects', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    return res.json();
};

// Отправить приглашение
const sendInvitation = async (projectId, userId, message) => {
    const token = localStorage.getItem('token');
    const res = await fetch(`http://localhost:8000/api/v1/projects/${projectId}/invitations`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ user_id: userId, message })
    });
    return res.json();
};
```

---

## Структура проекта

```
Clarity/
├── alembic/                      # Миграции Alembic
│   ├── versions/
│   │   └── 5176abe5d497_.py      # Пустая ревизия (таблицы созданы вручную)
│   ├── env.py                    # Конфигурация окружения Alembic
│   └── script.py.mako            # Шаблон для генерации миграций
├── api/
│   └── v1/
│       ├── __init__.py
│       ├── auth.py               # Роутеры аутентификации
│       ├── projects.py           # Роутеры проектов
│       ├── tasks.py              # Роутеры задач
│       ├── invitations.py        # Роутеры приглашений
│       └── user.py               # Роутеры профиля пользователя
├── core/
│   ├── __init__.py
│   ├── config.py                 # Настройки (pydantic-settings)
│   ├── database.py               # Подключение к БД (async engine, session)
│   ├── dependencies.py           # Зависимости (получение БД, текущий пользователь)
│   ├── exceptions.py             # Кастомные исключения и обработчики
│   └── security.py               # Хеширование, JWT
├── models/                       # SQLAlchemy модели
│   ├── __init__.py
│   ├── user.py
│   ├── project.py
│   ├── task.py
│   ├── project_members.py
│   └── project_invitations.py
├── repositories/                 # Слой доступа к данным
│   ├── __init__.py
│   ├── base.py                   # Базовый репозиторий (CRUD)
│   ├── user_repository.py
│   ├── project_repository.py
│   ├── task_repository.py
│   └── project_invitation_repository.py
├── schemas/                      # Pydantic схемы
│   ├── __init__.py
│   ├── auth.py
│   ├── user.py
│   ├── project.py
│   ├── task.py
│   ├── common.py                 # Enum-ы (TaskStatus, ProjectRole, InvitationRole)
│   └── invitation.py
├── services/                     # Бизнес-логика
│   ├── __init__.py
│   ├── auth_service.py
│   ├── project_service.py
│   ├── task_service.py
│   ├── project_members_service.py
│   ├── invitation_service.py
│   └── user_service.py
├── tests/                        # Тесты
│   ├── __init__.py
│   ├── conftest.py               # Фикстуры и настройка pytest (полностью готова)
│   ├── test_api/                 # Тесты API
│   │   ├── test_auth.py          # Тесты аутентификации
│   │   ├── test_projects.py      # Тесты проектов
│   │   ├── test_tasks.py         # Тесты задач
│   │   ├── test_invitations.py   # Тесты приглашений
│   │   └── test_profile.py       # Тесты профиля
│   ├── test_repositories/        # Тесты репозиториев (в разработке)
│   └── test_services/            # Тесты сервисов (в разработке)
├── utils/                        # Вспомогательные утилиты
│   ├── __init__.py
│   ├── decorators.py             # Декоратор @log для логирования
│   └── logger_setup.py           # (в будущем) настройка логирования
├── .env                          # Переменные окружения (не в репозитории)
├── .env.test                     # Переменные окружения для тестов
├── alembic.ini                   # Конфигурация Alembic
├── docker-compose.yml            # Конфигурация Docker Compose
├── Dockerfile                    # Dockerfile для сборки образа бэкенда
├── entrypoint.sh                 # Скрипт входа (выполняет миграции и запускает приложение)
├── main.py                       # Точка входа FastAPI
├── README.md                     # Этот файл
└── requirements.txt              # Зависимости Python
```

---

## Лицензия

Этот проект является открытым и распространяется под лицензией MIT.
