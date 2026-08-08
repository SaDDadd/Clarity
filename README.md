# TaskToDo – Бэкенд для управления проектами и задачами

Этот репозиторий содержит серверную часть (API) для системы управления проектами и задачами. Проект построен на **FastAPI** с использованием асинхронной **SQLAlchemy**, **MySQL**, **JWT-аутентификации** и **Alembic** для миграций. Бэкенд предоставляет RESTful API, которое может использоваться любым фронтендом (веб, мобильное приложение и т.д.).

---

## 📋 Содержание

- [Основные возможности](#-основные-возможности)
- [Используемые технологии](#-используемые-технологии)
- [Установка и запуск](#-установка-и-запуск)
- [Переменные окружения](#-переменные-окружения)
- [Миграции базы данных](#-миграции-базы-данных)
- [API Документация](#-api-документация)
  - [Аутентификация](#аутентификация)
  - [Проекты](#проекты)
  - [Задачи](#задачи)
  - [Приглашения](#приглашения)
- [Инструкция для фронтенда](#-инструкция-для-фронтенда)
- [Структура проекта](#-структура-проекта)
- [Планы по доработке](#-планы-по-доработке)

---

## 🚀 Основные возможности

- Регистрация и аутентификация пользователей с выдачей JWT-токена.
- Создание, просмотр, обновление и удаление проектов (только администратор проекта может редактировать/удалять).
- Управление участниками проекта (добавление/удаление – только админ).
- Создание, просмотр, обновление и удаление задач внутри проекта.
- Назначение задач пользователям, изменение статуса задач (`pending`, `in_progress`, `completed`).
- Получение задач, назначенных текущему пользователю.
- **Приглашения в проекты** – администратор может приглашать пользователей, те могут принимать или отклонять приглашения, после чего автоматически добавляются в проект.
- Встроенная документация OpenAPI (доступна по адресу `/docs`).

---

## 🛠 Используемые технологии

- **Python 3.11+**
- **FastAPI** – веб-фреймворк
- **SQLAlchemy** (асинхронный) – ORM
- **MySQL** – база данных (через `aiomysql`)
- **Alembic** – миграции
- **python-jose** – JWT
- **bcrypt** – хеширование паролей
- **Pydantic** – валидация данных
- **Uvicorn** – ASGI-сервер

---

## ⚙️ Установка и запуск

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/your-username/task-to-do-backend.git
cd task-to-do-backend
```

### 2. Создайте и активируйте виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
# или
venv\Scripts\activate      # Windows
```

### 3. Установите зависимости
```bash
pip install -r requirements.txt
```
> Если файл `requirements.txt` отсутствует, создайте его со следующим содержимым:
> ```
> fastapi
> uvicorn[standard]
> sqlalchemy
> aiomysql
> alembic
> python-jose[cryptography]
> bcrypt
> pydantic-settings
> python-dotenv
> ```

### 4. Настройте базу данных MySQL
- Убедитесь, что MySQL запущен.
- Создайте базу данных, например:
```sql
CREATE DATABASE task_to_do CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

> **Примечание:** На данный момент таблицы созданы вручную через MySQL Workbench. Миграции Alembic настроены, но текущая ревизия пуста. В дальнейшем все изменения схемы будут выполняться через миграции.

### 5. Настройте переменные окружения
Создайте файл `.env` в корне проекта (см. [Переменные окружения](#-переменные-окружения)).

### 6. Примените миграции (если они есть)
```bash
alembic upgrade head
```
Если миграции отсутствуют, этот шаг можно пропустить.

### 7. Запустите сервер
```bash
uvicorn main:app --reload
```

Сервер будет доступен по адресу: `http://localhost:8000`  
Документация API: `http://localhost:8000/docs`

---

## 🔐 Переменные окружения (файл `.env`)

Пример содержимого `.env`:
```env
# База данных
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=task_to_do
DB_DRIVER=aiomysql   # можно оставить по умолчанию

# JWT
JWT_SECRET_KEY=your_secret_key_here   # сгенерируйте надёжный ключ
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (опционально, для продакшена укажите конкретные домены)
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

Все настройки загружаются из класса `Settings` в `core/config.py`.  
Значение `JWT_SECRET_KEY` **обязательно** должно быть задано в `.env`.

---

## 🗄️ Миграции базы данных

Для управления схемой используется Alembic. В настоящее время миграции настроены, но первая ревизия пуста (таблицы созданы вручную). Для будущих изменений:

- **Создать новую миграцию** (после изменения моделей):
```bash
alembic revision --autogenerate -m "описание изменений"
```
- **Применить миграции**:
```bash
alembic upgrade head
```
- **Откатиться на предыдущую версию**:
```bash
alembic downgrade -1
```

---

## 📚 API Документация

Все эндпоинты имеют префикс `/api/v1`.  
Полная интерактивная документация доступна по адре `/docs` (Swagger UI) или `/redoc`.

Ниже приведён список основных эндпоинтов с примерами запросов/ответов.

### 🔐 Аутентификация

| Метод | Эндпоинт               | Описание                     |
|-------|------------------------|------------------------------|
| POST  | `/auth/register`       | Регистрация нового пользователя |
| POST  | `/auth/login`          | Вход в систему (получение токена) |
| GET   | `/auth/me`             | Получить информацию о текущем пользователе |

#### Регистрация
**Запрос:**
```json
POST /api/v1/auth/register
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password"
}
```
**Ответ (201 Created):**
```json
{
  "message": "Пользователь создан"
}
```

#### Логин
**Запрос:**
```json
POST /api/v1/auth/login
{
  "username_or_email": "john_doe",  // или email
  "password": "secure_password"
}
```
**Ответ (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Получение профиля
**Запрос:** `GET /api/v1/auth/me`  
**Заголовок:** `Authorization: Bearer <token>`

**Ответ (200 OK):**
```json
{
  "user_id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_date": "2026-08-07T20:13:03"
}
```

---

### 📁 Проекты

Все эндпоинты проектов требуют аутентификации (токен в заголовке).

| Метод   | Эндпоинт                           | Описание                                      |
|---------|------------------------------------|-----------------------------------------------|
| GET     | `/projects`                        | Список проектов, где пользователь – админ      |
| GET     | `/projects/all`                    | Список всех проектов, где пользователь участник (включая админа) |
| POST    | `/projects`                        | Создать новый проект                           |
| GET     | `/projects/{project_id}`           | Получить информацию о проекте (с участниками) |
| PUT     | `/projects/{project_id}`           | Обновить название/описание (только админ)      |
| DELETE  | `/projects/{project_id}`           | Удалить проект (только админ)                 |
| POST    | `/projects/{project_id}/members`   | Добавить участника в проект (только админ)    |
| DELETE  | `/projects/{project_id}/members`   | Удалить участника из проекта (только админ)   |

#### Создание проекта
**Запрос:**
```json
POST /api/v1/projects
{
  "project_name": "Новый проект",
  "project_description": "Описание проекта"
}
```
**Ответ (200 OK):** возвращает созданный объект проекта.

#### Получение проекта
**Запрос:** `GET /api/v1/projects/1`

**Ответ:**
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
      "email": "john@example.com",
      "created_date": "..."
    },
    ...
  ]
}
```

#### Добавление участника
**Запрос:**
```json
POST /api/v1/projects/1/members
{
  "user_id": 2
}
```
**Ответ:**
```json
{
  "message": "Пользователь добавлен в проект!"
}
```

---

### ✅ Задачи

| Метод   | Эндпоинт                                      | Описание                                   |
|---------|-----------------------------------------------|--------------------------------------------|
| GET     | `/projects/{project_id}/tasks`                | Получить все задачи проекта                 |
| POST    | `/projects/{project_id}/tasks`                | Создать задачу в проекте                   |
| GET     | `/projects/{project_id}/tasks/{task_id}`      | Получить детали задачи                     |
| PUT     | `/projects/{project_id}/tasks/{task_id}`      | Обновить задачу (любой участник проекта)   |
| PATCH   | `/projects/{project_id}/tasks/{task_id}/status` | Изменить статус задачи (любой участник)  |
| DELETE  | `/projects/{project_id}/tasks/{task_id}`      | Удалить задачу (только админ проекта)      |
| GET     | `/tasks`                                      | Получить задачи, назначенные текущему пользователю |

#### Создание задачи
**Запрос:**
```json
POST /api/v1/projects/1/tasks
{
  "title": "Написать документацию",
  "task_description": "Описание задачи",
  "task_status": "pending",       // или "in_progress", "completed"
  "assigned_to": 2,               // ID пользователя (опционально)
  "deadline": "2026-09-01"        // в формате YYYY-MM-DD
}
```
**Ответ:** возвращает созданную задачу.

#### Изменение статуса
**Запрос:**
```json
PATCH /api/v1/projects/1/tasks/1/status
{
  "task_status": "completed"
}
```
**Ответ:**
```json
{
  "message": "Статус обновлен!"
}
```

---

### 📨 Приглашения

Эндпоинты для приглашений полностью реализованы. Все требуют аутентификации.

| Метод   | Эндпоинт                                 | Описание                                      |
|---------|------------------------------------------|-----------------------------------------------|
| POST    | `/projects/{project_id}/invitations`     | Отправить приглашение в проект (только админ) |
| PATCH   | `/invitations/{invitation_id}`           | Принять/отклонить приглашение (только приглашённый) |
| GET     | `/invitations`                           | Список приглашений для текущего пользователя (входящие) |
| GET     | `/invitations/project/{project_id}`      | Список приглашений проекта (только админ)     |
| DELETE  | `/invitations/{invitation_id}`           | Отменить приглашение (админ или отправитель)  |

#### Отправка приглашения
**Запрос:**
```json
POST /api/v1/projects/1/invitations
{
  "user_id": 3,
  "message": "Присоединяйся к нашему проекту!"
}
```
**Ответ (200 OK):** возвращает созданный объект приглашения.

#### Ответ на приглашение
**Запрос:**
```json
PATCH /api/v1/invitations/1
{
  "action": "accepted"   // или "declined"
}
```
**Ответ:**
```json
{
  "message": "Приглашение accepted"
}
```
При успешном принятии пользователь автоматически добавляется в проект как участник.

#### Получение списка приглашений пользователя
**Запрос:** `GET /api/v1/invitations`

**Ответ:**
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

#### Отмена приглашения
**Запрос:** `DELETE /api/v1/invitations/1`

**Ответ:**
```json
{
  "message": "Приглашение отменено"
}
```

---

## 🖥️ Инструкция для фронтенда

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
- Все даты передаются в формате ISO 8601 (`YYYY-MM-DD` для дат без времени, `YYYY-MM-DDTHH:MM:SS` для datetime).
- Enum-поля (статусы задач, роли) передаются строками:
  - `task_status`: `"pending"`, `"in_progress"`, `"completed"`
  - `role_project` (в ответах): `"admin"`, `"member"`
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

## 🧱 Структура проекта

```
task-to-do-backend/
├── alembic/                 # Миграции Alembic
├── api/
│   └── v1/
│       ├── auth.py          # Роутеры аутентификации
│       ├── projects.py      # Роутеры проектов
│       ├── tasks.py         # Роутеры задач
│       └── invitations.py   # Роутеры приглашений
├── core/
│   ├── config.py            # Настройки (pydantic-settings)
│   ├── database.py          # Подключение к БД (async engine, session)
│   ├── dependencies.py      # Зависимости (получение БД, текущий пользователь)
│   ├── exceptions.py        # Кастомные исключения и обработчики
│   └── security.py          # Хеширование, JWT
├── models/                  # SQLAlchemy модели
│   ├── user.py
│   ├── project.py
│   ├── task.py
│   ├── project_members.py
│   └── project_invitations.py
├── repositories/            # Слой доступа к данным
│   ├── base.py
│   ├── user_repository.py
│   ├── project_repository.py
│   ├── task_repository.py
│   └── project_invitation_repository.py
├── schemas/                 # Pydantic схемы
│   ├── auth.py
│   ├── user.py
│   ├── project.py
│   ├── task.py
│   ├── common.py
│   └── invitation.py
├── services/                # Бизнес-логика
│   ├── auth_service.py
│   ├── project_service.py
│   ├── task_service.py
│   ├── user_service.py
│   └── invitation_service.py
├── utils/                   # Вспомогательные утилиты (декораторы, логирование)
├── .env                     # Переменные окружения (не в репозитории)
├── .env.example             # Шаблон .env (опционально)
├── alembic.ini              # Конфигурация Alembic
├── main.py                  # Точка входа FastAPI
└── requirements.txt         # Зависимости Python
```

---

## 📌 Планы по доработке

- [ ] **Чат проекта** – обмен сообщениями между участниками.
- [ ] **Уведомления** – оповещения о событиях (приглашения, изменения задач).
- [ ] **Фильтрация задач** – по статусу, проекту, датам и т.д.
- [ ] **Процент готовности проекта** – расчёт завершённости.
- [ ] **Контейнеризация** – Dockerfile + docker-compose для быстрого запуска.
- [ ] **Юнит-тесты** – pytest + httpx.
- [ ] **Логирование** – запись в файл/ELK (есть базовая реализация декоратора `log`).

Следите за обновлениями в репозитории!

---

## 📄 Лицензия

Этот проект является учебным и распространяется без лицензии (или укажите свою).

---

**Связь:** Если у вас возникли вопросы по API или предложения по улучшению, создавайте issue в репозитории.
```
**Связь:** Если у вас возникли вопросы по API или предложения по улучшению, создавайте issue в репозитории.
```
