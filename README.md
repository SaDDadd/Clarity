# Clarity — Task Management API

**Clarity** — это серверная часть (бэкенд) для системы управления проектами и задачами. Проект построен на **FastAPI** с использованием асинхронной **SQLAlchemy**, **MySQL**, **JWT-аутентификации** и **Alembic** для миграций. Бэкенд предоставляет RESTful API, которое может использоваться любым фронтендом (веб, мобильное приложение и т.д.).

## Содержание

- [Основные возможности](#основные-возможности)
- [Разграничение прав пользователей](#разграничение-прав-пользователей)
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
  - [Пользователи](#пользователи)
- [Тестирование](#тестирование)
- [Нагрузочное тестирование](#нагрузочное-тестирование)
- [Структура проекта](#структура-проекта)
- [Планы на доработку](#планы-на-доработку)

## Основные возможности

- Регистрация и аутентификация пользователей (JWT).
- Управление проектами (создание, просмотр, обновление, удаление).
- Ролевая модель: **admin**, **curator** и **member** в рамках проекта.
- Управление задачами внутри проектов (CRUD, смена статуса).
- Приоритет задачи (low / medium / high) и флаг «избранное».
- Комментирование задач (создание, редактирование и удаление комментариев).
- Приглашения пользователей в проекты.
- Профиль пользователя (смена имени, email, пароля и получение данных профиля).
- Поиск пользователей по нику.
- Получение информации о текущем пользователе через `/auth/me` и `/profile`.
- Инфраструктура кэширования на Redis (в разработке).
- Пагинация для списков (реализована, но не задокументирована — будет добавлена в следующих релизах).
- Полностью асинхронный код.
- Docker-контейнеризация.
- Написанные тесты (pytest + httpx).
- Нагрузочное тестирование с использованием Locust.

## Разграничение прав пользователей

В проекте предусмотрены три роли в рамках каждого проекта: **admin**, **curator** и **member**.

| Действие | Кто может |
|----------|-----------|
| Просмотр проекта | Все участники проекта |
| Просмотр списка задач проекта | Все участники проекта |
| Просмотр деталей задачи | Все участники проекта |
| Создание задачи | Все участники проекта |
| Обновление задачи | Все; member — только если он исполнитель задачи |
| Смена статуса задачи | Все; member — только если он исполнитель задачи |
| Удаление задачи | Только admin/curator |
| Создание комментариев | Все участники проекта |
| Редактирование/удаление комментария | Все; member — только свой комментарий |
| Ответ на приглашение | Все, но фактически только адресат приглашения |
| Отправка приглашения | Все участники проекта |
| Отмена приглашения | Все; member — только если он отправитель приглашения |
| Просмотр приглашений проекта | Все участники проекта |
| Обновление проекта | Только admin/curator |
| Добавление участника | Только admin/curator |
| Удаление участника | Только admin/curator; нельзя удалить admin |
| Изменение роли участника | Только admin/curator; можно менять роль любого участника, кроме admin; роль admin никто менять не может |
| Удаление проекта | Только admin |

## Используемые технологии

- **Python 3.10+**
- **FastAPI** — веб-фреймворк
- **SQLAlchemy** (асинхронный) — ORM
- **MySQL** — база данных
- **Alembic** — миграции
- **Pydantic** — валидация данных
- **python-jose** — JWT
- **bcrypt / aiobcrypt** — хеширование паролей (синхронное и асинхронное)
- **Redis** — кэширование (в разработке)
- **pytest + httpx** — тестирование
- **Locust** — нагрузочное тестирование
- **Docker / Docker Compose** — контейнеризация

## Архитектура проекта

Проект построен по многослойной архитектуре:

- **API слой** — роутеры FastAPI.
- **Слой сервисов** — бизнес-логика.
- **Репозитории** — работа с базой данных.
- **Модели** — SQLAlchemy-модели.
- **Схемы** — Pydantic-схемы для валидации запросов и ответов.
- **Ядро** — конфигурация, безопасность, зависимости, исключения.
- **Кэш** — обёртки над Redis (в разработке).

Такая структура обеспечивает **разделение ответственности**, упрощает тестирование и поддержку кода.

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
   source venv/bin/activate  # для Linux/Mac
   # или
   venv\Scripts\activate  # для Windows
   ```

3. **Установите зависимости:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Создайте файл `.env`** (см. раздел [Переменные окружения](#переменные-окружения-файл-env)).

5. **Запустите MySQL** (локально или в контейнере) и создайте базу данных.

6. **Создайте (при необходимости) и примените миграции Alembic:**

   ```bash
   alembic revision --autogenerate -m "имя миграции"
   alembic upgrade head
   ```

7. **Запустите приложение:**

   ```bash
   uvicorn main:app --reload
   ```

API будет доступно по адресу `http://localhost:8000`.

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

4. Для локальной раздачи статического фронтенда (если он находится в корне проекта) в отдельном терминале:

   ```bash
   python -m http.server 5500
   ```

5. Остановка:

   ```bash
   docker-compose down
   ```

> **Важно:** при использовании Docker переменные окружения загружаются из файла `.env`. Убедитесь, что все необходимые переменные заданы.

## Переменные окружения (файл `.env`)

Пример содержимого `.env`:

```env
# База данных
DB_HOST=db  # для Docker – имя сервиса db; для локального запуска – localhost
DB_PORT=3306  # порт внутри контейнера; при локальном запуске обычно 3306
DB_USER=root
DB_PASSWORD=your_secure_password
DB_NAME=task_to_do
DB_DRIVER=aiomysql

# JWT
JWT_SECRET_KEY=your_super_secret_key_here  # обязательно задайте надёжный ключ
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis (опционально, для кэширования)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# CORS (опционально)
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

Все настройки загружаются из класса `Settings` в `core/config.py`. Значение `JWT_SECRET_KEY` **обязательно** должно быть задано в `.env`.

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

Он подключается в `core/config.py` через `SettingsTEST` (при установленной переменной окружения `ENV=test` подгружается `.env.test`).

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

В проекте есть следующие миграции:

- `4ed2a0e57d1c_init.py` — начальная миграция (создаёт таблицы `users`, `projects`, `project_members`, `tasks`, `project_invitations`).
- `38152136d0e1_add_task_favorite.py` — добавляет поле `tasks.task_favorite` и обновляет `server_default` для `created_date`, `update_date`, `joined_date`.
- `80c4be0200f2_update_columns.py` — обновляет `server_default` и `NOT NULL` для полей дат и `status_invited`.
- `68e4603380d9_add_ondelete_cascade_in_project_.py` — добавляет `ON DELETE CASCADE` для внешних ключей в `project_invitations` и `project_members`.
- `93875e2f15c8_add_task_comments_and_update_admin_id_.py` — создаёт таблицу `task_comments`, переименовывает поле `admin_id` в `owner_id` в таблице `projects`.
- `ec45a763898f_updating_the_role_model_in_the_project.py` — обновляет ролевую модель в проекте, возвращает поле `admin_id` (переименовывает `owner_id` обратно в `admin_id`) и создаёт `task_comments` (если ещё не создана).

## Описание таблиц базы данных

Схема базы данных состоит из пяти таблиц, описанных ниже.

### Таблица `users` (пользователи)

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `user_id` | `int` | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `username` | `varchar(50)` | NOT NULL, UNIQUE | Имя пользователя |
| `email` | `varchar(100)` | NOT NULL, UNIQUE | Электронная почта |
| `password_hash` | `varchar(255)` | NOT NULL | Хеш пароля |
| `created_date` | `timestamp` | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Дата регистрации |

### Таблица `projects` (проекты)

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `project_id` | `int` | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `project_name` | `varchar(100)` | NOT NULL | Название проекта |
| `project_description` | `text` | YES | Описание проекта |
| `admin_id` | `int` | NOT NULL, FOREIGN KEY | ID создателя (админа) |

### Таблица `project_members` (участники проектов)

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `project_id` | `int` | NOT NULL, FOREIGN KEY | ID проекта |
| `user_id` | `int` | NOT NULL, FOREIGN KEY | ID пользователя |
| `role_project` | `enum` | NOT NULL, DEFAULT 'member' | Роль (`admin`, `curator` или `member`) |
| `joined_date` | `timestamp` | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Дата присоединения |

### Таблица `tasks` (задачи)

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `task_id` | `int` | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `title` | `varchar(150)` | NOT NULL | Название задачи |
| `task_description` | `text` | YES | Описание задачи |
| `task_status` | `enum('pending','in_progress','completed')` | YES, DEFAULT 'pending' | Статус задачи |
| `task_priority` | `enum('low','medium','high')` | NOT NULL, DEFAULT 'low' | Приоритет задачи |
| `task_favorite` | `bool` | NOT NULL, DEFAULT 0 | Флаг «избранное» |
| `project_id` | `int` | NOT NULL, FOREIGN KEY | ID проекта |
| `assigned_to` | `int` | YES, FOREIGN KEY | ID исполнителя |
| `deadline` | `date` | YES | Срок выполнения |
| `created_date` | `timestamp` | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Дата создания |

### Таблица `project_invitations` (приглашения)

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `invitation_id` | `int` | PRIMARY KEY, AUTO_INCREMENT | Уникальный идентификатор |
| `project_id` | `int` | NOT NULL, FOREIGN KEY | ID проекта |
| `inviter_id` | `int` | NOT NULL, FOREIGN KEY | ID пригласившего |
| `invitee_id` | `int` | NOT NULL, FOREIGN KEY | ID приглашённого |
| `status_invited` | `enum('pending','accepted','declined')` | YES, DEFAULT 'pending' | Статус приглашения |
| `created_date` | `timestamp` | YES, DEFAULT CURRENT_TIMESTAMP | Дата создания |
| `update_date` | `timestamp` | YES, DEFAULT CURRENT_TIMESTAMP | Дата последнего обновления |
| `message` | `text` | YES | Сообщение к приглашению |

## Документация API

**Базовый URL:** `http://localhost:8000/api/v1`

Все эндпоинты, кроме регистрации и логина, требуют **JWT-аутентификации**. Токен передаётся в заголовке:

```
Authorization: Bearer <token>
```

### Аутентификация

| Метод | Эндпоинт | Описание | Требует аутентификации |
|-------|----------|----------|------------------------|
| POST | `/auth/register` | Регистрация нового пользователя | ❌ |
| POST | `/auth/login` | Вход в систему (получение токена) | ❌ |
| POST | `/auth/token` | Логин для Swagger (OAuth2PasswordRequestForm) | ❌ |

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
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Ошибки:**

- `401 Unauthorized` — неверные учётные данные.
- `422 Unprocessable Entity` — пустые поля.

#### Логин для Swagger

**Запрос:**

```http
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

username=john_doe&password=securepassword123
```

**Успешный ответ (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Получение информации о текущем пользователе

**Запрос:**

### Проекты

| Метод | Эндпоинт | Описание | Требует аутентификации | Роль |
|-------|----------|----------|------------------------|------|
| POST | `/projects` | Создать проект | ✅ | - |
| GET | `/projects` | Список проектов, где пользователь — админ | ✅ | - |
| GET | `/projects/all` | Список всех проектов, где пользователь участвует | ✅ | - |
| GET | `/projects/{project_id}` | Получить информацию о проекте | ✅ | member/admin/curator |
| PUT | `/projects/{project_id}` | Обновить проект | ✅ | admin/curator |
| DELETE | `/projects/{project_id}` | Удалить проект | ✅ | admin |
| POST | `/projects/{project_id}/members` | Добавить участника в проект | ✅ | admin/curator |
| DELETE | `/projects/{project_id}/members/{user_id}` | Удалить участника из проекта | ✅ | admin/curator |
| PATCH | `/projects/{project_id}/members/{user_id}/role` | Изменить роль участника | ✅ | admin/curator |

#### Создание проекта

**Запрос:**

```http
POST /api/v1/projects
Authorization: Bearer <token>
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

#### Получение списка проектов (где пользователь — админ)

**Запрос:**

```http
GET /api/v1/projects
Authorization: Bearer <token>
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

#### Получение списка всех проектов пользователя (админ + участник)

**Запрос:**

```http
GET /api/v1/projects/all
Authorization: Bearer <token>
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

#### Получение информации о проекте

**Запрос:**

```http
GET /api/v1/projects/1
Authorization: Bearer <token>
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
      "role": "admin",
      "joined_date": "2026-08-20T10:00:00"
    },
    {
      "user_id": 2,
      "role": "member",
      "joined_date": "2026-08-20T10:05:00"
    }
  ]
}
```

**Ошибки:**

- `404 Not Found` — проект не найден.
- `403 Forbidden` — пользователь не является участником проекта.

#### Обновление проекта

**Запрос:**

```http
PUT /api/v1/projects/1
Authorization: Bearer <token>
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

- `403 Forbidden` — пользователь не админ/куратор проекта.
- `404 Not Found` — проект не найден.

#### Удаление проекта

**Запрос:**

```http
DELETE /api/v1/projects/1
Authorization: Bearer <token>
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

#### Добавление участника в проект

**Запрос:**

```http
POST /api/v1/projects/1/members
Authorization: Bearer <token>
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
- `403 Forbidden` — пользователь не админ/куратор проекта.
- `404 Not Found` — пользователь не найден.
- `409 Conflict` — пользователь уже состоит в проекте.

#### Удаление участника из проекта

**Запрос:**

```http
DELETE /api/v1/projects/1/members/2
Authorization: Bearer <token>
```

**Успешный ответ (200 OK):**

```json
{
  "message": "Пользователь удален из проекта!"
}
```

**Ошибки:**

- `400 Bad Request` — попытка удалить самого себя (единственного админа).
- `403 Forbidden` — пользователь не админ/куратор проекта.
- `409 Conflict` — пользователь не состоит в проекте.

#### Изменение роли участника

**Запрос:**

```http
PATCH /api/v1/projects/1/members/2/role?role=admin
Authorization: Bearer <token>
```

**Успешный ответ (200 OK):**

```json
{
  "message": "Роль обновлена"
}
```

**Ошибки:**

- `400 Bad Request` — попытка понизить единственного админа.
- `403 Forbidden` — пользователь не админ/куратор проекта.

### Задачи

| Метод | Эндпоинт | Описание | Требует аутентификации | Роль |
|-------|----------|----------|------------------------|------|
| GET | `/tasks` | Получить задачи, назначенные текущему пользователю | ✅ | - |
| GET | `/projects/{project_id}/tasks` | Получить все задачи проекта | ✅ | member/admin/curator |
| GET | `/projects/{project_id}/tasks/{task_id}` | Получить детали задачи | ✅ | member/admin/curator |
| POST | `/projects/{project_id}/tasks` | Создать задачу в проекте | ✅ | member/admin/curator |
| PUT | `/projects/{project_id}/tasks/{task_id}` | Обновить задачу | ✅ | member/admin/curator* |
| PATCH | `/projects/{project_id}/tasks/{task_id}/status` | Изменить статус задачи | ✅ | member/admin/curator* |
| DELETE | `/projects/{project_id}/tasks/{task_id}` | Удалить задачу | ✅ | admin/curator |

> \* member может обновлять задачу и менять её статус только если он назначен исполнителем этой задачи.

#### Создание задачи

**Запрос:**

```http
POST /api/v1/projects/1/tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Написать документацию",
  "task_description": "Описание задачи",
  "task_status": "pending",           // "pending" | "in_progress" | "completed"
  "task_priority": "low",             // "low" | "medium" | "high"
  "task_favorite": false,
  "assigned_to": 2,                   // ID пользователя (опционально)
  "deadline": "2026-09-01"            // в формате YYYY-MM-DD
}
```

**Успешный ответ (201 Created):**

```json
{
  "task_id": 1,
  "title": "Написать документацию",
  "task_description": "Описание задачи",
  "task_status": "pending",
  "task_priority": "low",
  "task_favorite": false,
  "project_id": 1,
  "assigned_to": 2,
  "deadline": "2026-09-01",
  "created_date": "2026-08-20T10:00:00"
}
```

#### Получение всех задач проекта

**Запрос:**

```http
GET /api/v1/projects/1/tasks
Authorization: Bearer <token>
```

**Успешный ответ (200 OK):**

```json
[
  {
    "task_id": 1,
    "title": "Написать документацию",
    "task_status": "pending",
    "task_priority": "low",
    "task_favorite": false,
    "assigned_to": 2,
    "deadline": "2026-09-01"
  }
]
```

#### Получение деталей задачи

**Запрос:**

```http
GET /api/v1/projects/1/tasks/1
Authorization: Bearer <token>
```

**Успешный ответ (200 OK):**

```json
{
  "task_id": 1,
  "title": "Написать документацию",
  "task_description": "Описание задачи",
  "task_status": "pending",
  "task_priority": "low",
  "task_favorite": false,
  "project_id": 1,
  "assigned_to": 2,
  "deadline": "2026-09-01",
  "created_date": "2026-08-20T10:00:00"
}
```

#### Обновление задачи

**Запрос:**

```http
PUT /api/v1/projects/1/tasks/1
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Обновлённый заголовок",
  "task_description": "Новое описание",
  "task_status": "in_progress",
  "task_priority": "high",
  "task_favorite": true,
  "assigned_to": 3,
  "deadline": "2026-10-01"
}
```

**Успешный ответ (200 OK):**

```json
{
  "message": "Задача обновилась!"
}
```

#### Изменение статуса задачи

**Запрос:**

```http
PATCH /api/v1/projects/1/tasks/1/status
Authorization: Bearer <token>
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

#### Удаление задачи

**Запрос:**

```http
DELETE /api/v1/projects/1/tasks/1
Authorization: Bearer <token>
```

**Успешный ответ (200 OK):**

```json
{
  "message": "Задача удалена из проекта!"
}
```

**Ошибки:**

- `403 Forbidden` — пользователь не админ/куратор проекта.

#### Получение задач, назначенных текущему пользователю

**Запрос:**

```http
GET /api/v1/tasks
Authorization: Bearer <token>
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

### Приглашения

| Метод | Эндпоинт | Описание | Требует аутентификации | Роль |
|-------|----------|----------|------------------------|------|
| POST | `/projects/{project_id}/invitations` | Отправить приглашение в проект | ✅ | member/admin/curator |
| GET | `/invitations` | Список входящих приглашений для пользователя | ✅ | - |
| GET | `/invitations/project/{project_id}` | Список приглашений проекта | ✅ | member/admin/curator |
| PATCH | `/invitations/{invitation_id}` | Принять/отклонить приглашение | ✅ | invitee (адресат) |
| DELETE | `/invitations/{invitation_id}` | Отменить приглашение | ✅ | member/admin/curator** |

> \*\* member может отменить приглашение, только если он является его отправителем; admin/curator могут отменить любое приглашение проекта.

#### Отправка приглашения

**Запрос:**

```http
POST /api/v1/projects/1/invitations
Authorization: Bearer <token>
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

#### Получение списка приглашений для пользователя

**Запрос:**

```http
GET /api/v1/invitations
Authorization: Bearer <token>
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

#### Получение списка приглашений проекта

**Запрос:**

```http
GET /api/v1/invitations/project/1
Authorization: Bearer <token>
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

#### Ответ на приглашение

**Запрос:**

```http
PATCH /api/v1/invitations/1
Authorization: Bearer <token>
Content-Type: application/json

{
  "action": "accepted"  // или "declined"
}
```

**Успешный ответ (200 OK):**

```json
{
  "message": "Приглашение accepted"
}
```

При успешном принятии пользователь автоматически добавляется в проект как участник.

#### Отмена приглашения

**Запрос:**

```http
DELETE /api/v1/invitations/1
Authorization: Bearer <token>
```

**Успешный ответ (200 OK):**

```json
{
  "message": "Приглашение отменено"
}
```

### Профиль пользователя

| Метод | Эндпоинт | Описание | Требует аутентификации |
|-------|----------|----------|------------------------|
| GET | `/profile` | Получить данные текущего пользователя | ✅ |
| PUT | `/profile/username` | Обновить имя пользователя | ✅ |
| PUT | `/profile/email` | Обновить email пользователя | ✅ |
| PATCH | `/profile/password` | Обновить пароль пользователя | ✅ |

#### Получение данных профиля

**Запрос:**

```http
GET /api/v1/profile
Authorization: Bearer <token>
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

#### Обновление имени

**Запрос:**

```http
PUT /api/v1/profile/username
Authorization: Bearer <token>
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

#### Обновление email

**Запрос:**

```http
PUT /api/v1/profile/email
Authorization: Bearer <token>
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

#### Обновление пароля

**Запрос:**

```http
PATCH /api/v1/profile/password
Authorization: Bearer <token>
Content-Type: application/json

{
  "password": "new_secure_password"
}
```

**Успешный ответ (200 OK):**

```json
{
  "message": "Пароль пользователя обновлен!"
}
```

### Пользователи

| Метод | Эндпоинт | Описание | Требует аутентификации |
|-------|----------|----------|------------------------|
| GET | `/users/search?search_user=...` | Поиск пользователя по нику | ✅ |

#### Поиск пользователя по нику

**Запрос:**

```http
GET /api/v1/users/search?search_user=john
Authorization: Bearer <token>
```

**Успешный ответ (200 OK):**

```json
[
  {
    "user_id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_date": "2026-08-20T10:00:00"
  }
]
```

**Ошибки:**

- `404 Not Found` — пользователь не найден.

> ⚠️ В коде репозитория (`UserRepository.search_by_username`) возвращается `list[dict]`, при этом сервис `search_by_username` в `services/user_service.py` типизирован как `UserModel | dict`. Проверьте фактический формат ответа.

## Тестирование

Для тестирования API используется **pytest** с асинхронной поддержкой и **httpx**. Все тесты находятся в директории `tests/` и покрывают основные сценарии работы с эндпоинтами, а также репозитории и сервисы.

Общее количество тестов: **324** — все успешно проходят.

### Структура тестов

```
tests/
├── conftest.py               # Фикстуры и настройка pytest
├── test_api/                 # Тесты API (109 тестов)
│   ├── test_auth.py
│   ├── test_projects.py
│   ├── test_tasks.py
│   ├── test_invitations.py
│   └── test_profile.py
├── test_repositories/        # Тесты репозиториев (97 тестов)
│   ├── test_user_repository.py
│   ├── test_project_repository.py
│   ├── test_task_repository.py
│   └── test_invitation_repository.py
└── test_services/            # Тесты сервисного слоя (118 тестов)
    ├── test_auth_service.py
    ├── test_invitation_service.py
    ├── test_project_member_service.py
    ├── test_project_service.py
    ├── test_task_service.py
    └── test_user_service.py
```

### Запуск тестов

1. Убедитесь, что создан файл `.env.test` с настройками для тестовой базы данных.
2. Запустите тесты:

   ```bash
   pytest -v
   ```

### Описание тестов

#### Тесты API (`test_api/`)

##### Тесты аутентификации (`test_auth.py`)

| Название теста | Описание |
|----------------|----------|
| `test_register_success` | Успешная регистрация нового пользователя. |
| `test_register_duplicate_username` | Попытка регистрации с уже существующим именем пользователя. |
| `test_register_duplicate_email` | Попытка регистрации с уже существующим email. |
| `test_login_success_username` | Успешный вход по имени пользователя. |
| `test_login_success_email` | Успешный вход по email. |
| `test_login_wrong_password` | Попытка входа с неверным паролем. |
| `test_login_user_not_found` | Попытка входа с несуществующим пользователем. |
| `test_login_empty_fields` | Попытка входа с пустыми полями. |
| `test_short_password` | Попытка регистрации с паролем короче 8 символов. |
| `test_get_current_user_info` | Получение информации о текущем пользователе через `/auth/me`. |
| `test_register_invalid_email` | Регистрация с невалидным email. |
| `test_register_empty_fields` | Регистрация с пустыми полями (username, email, password). |
| `test_login_empty_username` | Логин с пустым `username_or_email`. |
| `test_login_empty_password` | Логин с пустым `password`. |
| `test_get_current_user_unauthorized` | Запрос `/auth/me` без токена. |
| `test_get_current_user_invalid_token` | Запрос `/auth/me` с неверным токеном. |

##### Тесты проектов (`test_projects.py`)

| Название теста | Описание |
|----------------|----------|
| `test_successful_project_creation` | Успешное создание проекта. |
| `test_attempt_create_project_without_authorization` | Создание проекта без токена. |
| `test_attempt_create_project_with_incorrect_data` | Создание проекта с некорректными данными. |
| `test_authorized_admin_projects_returned` | Получение списка проектов, где пользователь — админ. |
| `test_attempt_get_non_existent_project` | Попытка получить несуществующий проект. |
| `test_attempt_get_project_that_user_not_part` | Попытка получить проект, в котором пользователь не состоит. |
| `test_authorized_user_projects_returned` | Получение всех проектов пользователя. |
| `test_getting_project_lets_project_participant_see_details` | Участник проекта получает его детали. |
| `test_admin_update_project` | Админ обновляет проект. |
| `test_updating_not_existent_project` | Попытка обновить несуществующий проект. |
| `test_deleting_not_existent_project` | Попытка удалить несуществующий проект. |
| `test_regular_participant_not_update_project` | Обычный участник не может обновить проект. |
| `test_admin_delete_project` | Админ удаляет проект. |
| `test_regular_participant_not_delete_project` | Обычный участник не может удалить проект. |
| `test_admin_add_existing_user` | Админ добавляет пользователя в проект. |
| `test_adding_yourself` | Попытка добавить самого себя. |
| `test_admin_not_add_user_already_in_project` | Попытка добавить уже существующего участника. |
| `test_admin_delete_anyone` | Админ удаляет участника. |
| `test_regular_member_not_delete_anyone` | Обычный участник не может удалить другого. |
| `test_admin_raise_or_lower_role` | Админ повышает/понижает роль. |
| `test_not_demote_only_admin` | Попытка понизить единственного админа. |
| `test_empty_projects_list_for_new_user` | Новый пользователь получает пустой список проектов. |
| `test_regular_member_add_user_to_project` | Обычный участник не может добавить пользователя. |
| `test_admin_add_non_existent_user` | Попытка добавить несуществующего пользователя. |
| `test_admin_delete_user_not_in_project` | Попытка удалить пользователя, не состоящего в проекте. |
| `test_member_projects_list` | Участник видит проекты, в которых состоит. |
| `test_regular_member_change_role` | Обычный участник не может изменить роль. |
| `test_add_user_to_non_existent_project` | Попытка добавить пользователя в несуществующий проект. |
| `test_update_project_with_no_changes` | Обновление проекта без изменений. |
| `test_update_project_user_not_member` | Попытка обновить проект пользователем, не состоящим в нём. |
| `test_admin_delete_self_from_project` | Попытка админа удалить самого себя (запрещено). |

##### Тесты задач (`test_tasks.py`)

| Название теста | Описание |
|----------------|----------|
| `test_creating_task_in_project_by_member` | Участник проекта создаёт задачу. |
| `test_attempt_create_task_by_non_participant` | Пользователь, не состоящий в проекте, не может создать задачу. |
| `test_getting_project_task_list` | Участник проекта получает список задач. |
| `test_getting_task_by_ID` | Получение конкретной задачи по ID. |
| `test_update_task` | Обновление задачи участником. |
| `test_delete_task` | Удаление задачи участником. |
| `test_changing_task_status` | Изменение статуса задачи. |
| `test_attempt_get_non_existent_task` | Запрос несуществующей задачи. |
| `test_create_task_with_deadline_in_past` | Создание задачи с дэдлайном в прошлом (ошибка). |
| `test_create_task_with_assigned_to_not_in_project` | Назначение задачи пользователю вне проекта. |
| `test_get_tasks_for_current_user` | Получение задач, назначенных на текущего пользователя. |
| `test_get_task_info_by_participant` | Получение информации о задаче участником. |
| `test_get_task_info_by_non_participant` | Не участник не может получить информацию о задаче. |
| `test_get_task_info_for_non_existent_task` | Получение информации о несуществующей задаче. |
| `test_update_task_by_admin` | Администратор обновляет задачу. |
| `test_update_task_by_member` | Участник обновляет задачу. |
| `test_update_task_with_invalid_deadline` | Обновление дэдлайна на прошедшую дату (ошибка). |
| `test_update_task_set_assigned_to_not_in_project` | Назначение задачи на пользователя вне проекта при обновлении. |
| `test_delete_task_by_admin` | Администратор удаляет задачу. |
| `test_delete_task_by_member` | Участник удаляет задачу (разрешено). |
| `test_change_status_to_valid` | Изменение статуса на допустимое значение. |
| `test_change_status_to_invalid` | Попытка установить недопустимый статус. |
| `test_change_status_of_non_existent_task` | Изменение статуса у несуществующей задачи. |
| `test_change_status_by_non_participant` | Не участник не может изменить статус задачи. |

##### Тесты приглашений (`test_invitations.py`)

| Название теста | Описание |
|----------------|----------|
| `test_send_invitation_by_admin` | Администратор отправляет приглашение. |
| `test_send_invitation_by_non_admin` | Участник (не админ) не может отправить приглашение. |
| `test_get_user_invitations` | Получение списка входящих приглашений для пользователя. |
| `test_get_project_invitations_by_admin` | Администратор получает список приглашений проекта. |
| `test_get_project_invitations_by_non_admin` | Участник (не админ) не может получить список приглашений проекта. |
| `test_accept_invitation` | Пользователь принимает приглашение. |
| `test_reject_invitation` | Пользователь отклоняет приглашение. |
| `test_cancel_invitation_by_admin` | Администратор отменяет приглашение. |
| `test_cancel_invitation_by_non_admin` | Участник (не админ) не может отменить приглашение. |
| `test_accept_already_processed_invitation` | Попытка принять уже обработанное приглашение. |
| `test_cancel_invitation_by_outsider` | Посторонний пользователь не может отменить приглашение. |
| `test_get_project_invitations_by_outsider` | Пользователь, не состоящий в проекте, не может получить список приглашений. |
| `test_send_invitation_to_existing_member` | Приглашение пользователя, уже состоящего в проекте. |
| `test_send_invitation_to_self` | Админ приглашает самого себя. |
| `test_send_invitation_to_nonexistent_user` | Приглашение несуществующего пользователя. |
| `test_reject_invitation_already_processed` | Отклонение уже принятого приглашения. |
| `test_accept_invitation_already_rejected` | Принятие уже отклонённого приглашения. |
| `test_cancel_invitation_already_processed` | Отмена уже принятого приглашения администратором. |
| `test_get_user_invitations_empty` | Пользователь без приглашений получает пустой список. |
| `test_get_project_invitations_empty` | Проект без приглашений возвращает пустой список. |

##### Тесты профиля (`test_profile.py`)

| Название теста | Описание |
|----------------|----------|
| `test_update_username_success` | Успешное обновление имени пользователя. |
| `test_update_username_unauthorized` | Запрос без токена. |
| `test_update_email_success` | Успешное обновление email. |
| `test_update_email_unauthorized` | Запрос без токена. |
| `test_get_profile_success` | Получение данных профиля. |
| `test_update_username_conflict` | Обновление username на уже существующий. |
| `test_update_email_conflict` | Обновление email на уже существующий. |
| `test_update_username_empty` | Обновление username на пустую строку. |
| `test_update_email_invalid` | Обновление email на невалидный. |
| `test_update_username_too_long` | Обновление username на слишком длинное значение. |
| `test_update_email_too_long` | Обновление email на слишком длинное значение. |
| `test_get_profile_unauthorized` | Запрос `/profile` без токена. |

#### Тесты репозиториев (`test_repositories/`)

| Файл | Описание | Количество тестов |
|------|----------|-------------------|
| `test_user_repository.py` | Тесты методов работы с пользователями (создание, поиск, обновление, удаление, проверка уникальности). | ~30 |
| `test_project_repository.py` | Тесты управления проектами и участниками (создание, добавление/удаление участников, роли, удаление проекта). | ~35 |
| `test_task_repository.py` | Тесты операций с задачами (создание, назначение, обновление, удаление, проверка принадлежности проекту). | ~19 |
| `test_invitation_repository.py` | Тесты управления приглашениями (создание, получение по пользователю/проекту, обновление статуса, удаление). | ~13 |

#### Тесты сервисов (`test_services/`)

| Файл | Описание | Количество тестов |
|------|----------|-------------------|
| `test_auth_service.py` | Тесты аутентификации и регистрации. | ~10 |
| `test_invitation_service.py` | Тесты логики приглашений. | ~17 |
| `test_project_member_service.py` | Тесты управления ролями участников. | ~7 |
| `test_project_service.py` | Тесты бизнес-логики проектов. | ~20 |
| `test_task_service.py` | Тесты бизнес-логики задач. | ~20 |
| `test_user_service.py` | Тесты обновления профиля пользователя. | ~10 |

### Описание основных фикстур (`conftest.py`)

| Фикстура | Описание |
|----------|----------|
| `sync_engine` | Создаёт синхронный движок SQLAlchemy (pymysql), создаёт все таблицы через `Base.metadata.create_all`. |
| `async_engine` | Создаёт асинхронный движок SQLAlchemy для тестов. |
| `db_session` | Создаёт новую сессию базы данных для каждого теста, откатывает транзакцию после. |
| `async_client` | Предоставляет асинхронный HTTP-клиент для тестирования эндпоинтов без запуска сервера. |
| `create_test_user` | Создаёт тестового пользователя с заданным паролем. |
| `test_users` | Создаёт четырёх тестовых пользователей: `admin`, `member`, `outsider`, `user_profile`. |
| `auth_headers` | Возвращает заголовки с JWT-токеном для пользователя `admin`. |
| `member_auth_headers` | Возвращает заголовки с JWT-токеном для пользователя `member`. |
| `test_project` | Создаёт тестовый проект с пользователем `admin` в роли администратора. |
| `test_project_with_member` | Создаёт тестовый проект и добавляет в него пользователя `member`. |
| `test_task` | Создаёт тестовую задачу в проекте. |
| `test_invitation` | Создаёт тестовое приглашение в проект. |

## Нагрузочное тестирование

Для проверки производительности и стабильности API реализован набор нагрузочных тестов с использованием **Locust**. Тесты расположены в директории `tests/load/` и позволяют симулировать одновременную работу нескольких сотен пользователей.

### Подготовка

1. Убедитесь, что все зависимости установлены (включая `locust` из `requirements.txt`).
2. Для нагрузочного тестирования используется отдельная тестовая база данных (настройки берутся из `.env.test`). Перед запуском тестов база данных будет заполнена тестовыми данными с помощью скрипта `seed_data.py`, который создаёт:
   - 500 пользователей,
   - 200 проектов,
   - участников в каждом проекте,
   - по 10 задач в каждом проекте.

### Запуск нагрузочного тестирования

Существует два способа запуска:

#### 1. Автоматический запуск через `run_load_test.py`

Этот скрипт запускает FastAPI-сервер в фоновом режиме, заполняет базу данных тестовыми данными и запускает Locust.

```bash
run_load_test
```

По умолчанию запускается в **интерактивном режиме** (открывается веб-интерфейс Locust). Чтобы запустить в **headless-режиме** (без UI), передайте любой аргумент, например:

```bash
run_load_test --headless
```

Можно также настроить параметры нагрузки, передав их в командной строке:

```bash
run_load_test --headless --users 200 --spawn-rate 20 --run-time 10m
```

Скрипт автоматически:

- Запускает сервер на `http://localhost:8000` с переменной окружения `ENV=test`.
- Ожидает готовности сервера.
- Заполняет БД тестовыми данными (вызов `seed_data.py`).
- Запускает Locust с переданными параметрами.
- После завершения теста останавливает сервер.

#### 2. Ручной запуск

Если вы хотите запустить сервер и Locust отдельно:

1. Установите переменную окружения `ENV=test` и запустите сервер:

   ```bash
   ENV=test uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. В другом терминале заполните БД тестовыми данными:

   ```bash
   python tests/load/seed_data.py
   ```

3. Запустите Locust:

   ```bash
   locust -f tests/load/locustfile.py --host=http://localhost:8000
   ```

   Откройте веб-интерфейс Locust по адресу `http://localhost:8089` и настройте нагрузку.

### Структура нагрузочных тестов

- `seed_data.py` — скрипт для генерации тестовых данных (пользователи, проекты, участники, задачи). Записывает логины/пароли пользователей в `tests/load/users.csv` для использования Locust.
- `locustfile.py` — сценарии поведения пользователей: получение списка проектов, создание/обновление/удаление проектов и задач, работа с приглашениями и т.д.
- `run_load_test.py` — вспомогательный скрипт для автоматического запуска сервера, заполнения БД и запуска Locust.

### Очистка данных

После завершения тестов все таблицы в тестовой БД будут очищены (триггер `test_stop` в Locust вызывает `truncate_tables()`).

> **Примечание:** Нагрузочное тестирование предназначено для проверки производительности и не должно использоваться на продакшн-базе данных.

## Структура проекта

```
Clarity/
├── alembic/                     # Миграции Alembic
│   ├── versions/
│   │   ├── 4ed2a0e57d1c_init.py                              # Начальная миграция
│   │   ├── 38152136d0e1_add_task_favorite.py                 # Добавлено поле task_favorite
│   │   ├── 80c4be0200f2_update_columns.py                    # Обновлены server_default и NOT NULL
│   │   ├── 68e4603380d9_add_ondelete_cascade_in_project_.py  # Добавлены ON DELETE CASCADE
│   │   ├── 93875e2f15c8_add_task_comments_and_update_admin_id_.py  # Создана task_comments
│   │   └── ec45a763898f_updating_the_role_model_in_the_project.py  # Обновлена ролевая модель
│   ├── env.py                    # Конфигурация окружения Alembic
│   └── script.py.mako            # Шаблон для генерации миграций
├── api/
│   └── v1/
│       ├── __init__.py
│       ├── auth.py               # Роутеры аутентификации
│       ├── projects.py           # Роутеры проектов
│       ├── tasks.py              # Роутеры задач
│       ├── invitations.py        # Роутеры приглашений
│       └── user.py               # Роутеры профиля (включая GET /profile, PATCH /profile/password, GET /users/search)
├── cache/                        # Обёртки Redis (в разработке)
│   ├── cache_keys.py             # Префиксы, TTL, функции формирования ключей
│   ├── cache_service.py          # get/set/delete + (в разработке) get_or_set, delete_cache_by_pattern
│   └── redis_client.py           # get_redis_client / close_redis_client / ping_redis
|   └── rate_limiter.py           # Модуль ограничения частоты запросов
├── core/
│   ├── __init__.py
│   ├── config.py                 # Настройки приложения (в т.ч. Redis)
│   ├── database.py               # Подключение к БД
│   ├── dependencies.py           # Dependency Injection, current_user, oauth2_scheme
│   ├── exceptions.py             # Кастомные исключения и обработчики
│   └── security.py               # JWT, хеширование (синхронное и асинхронное)
├── models/
│   ├── __init__.py
│   ├── user.py                   # Модель User
│   ├── project.py                # Модель Project
│   ├── project_members.py        # Модель ProjectMember
│   ├── task.py                   # Модель Task (с task_priority и task_favorite)
│   └── project_invitations.py    # Модель Invitation
├── repositories/
│   ├── __init__.py
│   ├── base.py                   # Базовый репозиторий
│   ├── user_repository.py
│   ├── project_repository.py
│   ├── task_repository.py
│   └── project_invitation_repository.py
├── schemas/
│   ├── __init__.py
│   ├── auth.py                   # Схемы для аутентификации
│   ├── project.py                # Схемы для проектов
│   ├── task.py                   # Схемы для задач
│   ├── invitation.py             # Схемы для приглашений
│   ├── user.py                   # Схемы для профиля
│   └── common.py                 # Общие перечисления (статусы, роли, приоритеты)
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── project_service.py
│   ├── task_service.py
│   ├── invitation_service.py
│   ├── project_members_service.py
│   └── user_service.py
├── tests/
│   ├── conftest.py               # Фикстуры для тестов
│   ├── test_api/                 # Тесты API (109 тестов)
│   │   ├── test_auth.py
│   │   ├── test_projects.py
│   │   ├── test_tasks.py
│   │   ├── test_invitations.py
│   │   └── test_profile.py
│   ├── test_repositories/        # Тесты репозиториев (97 тестов)
│   │   ├── test_user_repository.py
│   │   ├── test_project_repository.py
│   │   ├── test_task_repository.py
│   │   └── test_invitation_repository.py
│   ├── test_services/            # Тесты сервисного слоя (118 тестов)
│   │   ├── test_auth_service.py
│   │   ├── test_invitation_service.py
│   │   ├── test_project_member_service.py
│   │   ├── test_project_service.py
│   │   ├── test_task_service.py
│   │   └── test_user_service.py
│   └── load/                     # Нагрузочное тестирование
│       ├── locustfile.py         # Сценарии Locust
│       ├── seed_data.py          # Генерация тестовых данных
│       └── users.csv             # Сгенерированные учётные данные (создаётся автоматически)
├── .env                          # Пример файла окружения
├── .env.test                     # Файл окружения для тестов
├── ai_commit.py                  # ИИ помощник для комментариев коммитов
├── docker-compose.yaml
├── alembic.ini
├── entrypoint.sh
├── Dockerfile
├── requirements.txt
├── run_load_test.py               # Скрипт для автоматического запуска нагрузочных тестов
└── main.py                        # Точка входа
```

## Планы на доработку

Проект активно развивается. В ближайших релизах планируется:

- **Пагинации** — пагинация не реализована. Будет добавлено подробное описание с примерами запросов в будущем.
- **WebSocket-уведомления** — добавление реального времени: уведомления о новых задачах, изменениях статуса, приглашениях и комментариях.
- **Фильтрация и поиск** — расширенные возможности поиска задач по названию, статусу, исполнителю, приоритету и дедлайну.
- **Завершение кэширования на Redis** — в `cache/` сейчас реализованы только `get/set/delete` и заготовки ключей; нужно доделать инвалидацию (`delete_cache_by_pattern`) и комбинированный `get_or_set`, а также подключить кэш к роутерам.
- **CI/CD пайплайн** — настройка автоматического тестирования и деплоя через GitHub Actions.
- **Поддержка других БД** — добавление поддержки PostgreSQL для упрощения локальной разработки и тестирования.
- **Swagger/OpenAPI улучшения** — детальное описание всех эндпоинтов, схем и возможных ошибок для улучшения Developer Experience.
- **Rate Limiting** — защита API от чрезмерных запросов (в `cache_keys.py` уже предусмотрен префикс `RATE_LIMITING_PREFIX`).
- **Логирование** — внедрение структурированного логирования (например, через `structlog`) для упрощения отладки и мониторинга.
