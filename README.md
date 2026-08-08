Понял, вы хотите, чтобы README выглядел более профессионально и красиво на GitHub. Я доработал оформление: добавил **бейджи** (статус, версии, технологии), **цветные акценты**, **иконки**, **таблицы с выравниванием** и **структурированное оглавление**. Скопируйте этот текст в файл `README.md` – на GitHub он отобразится со всеми визуальными улучшениями.

---

```markdown
# 🚀 TaskToDo – Бэкенд для управления проектами и задачами

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Alembic](https://img.shields.io/badge/Alembic-1.13.0-FFD700?logo=alembic)](https://alembic.sqlalchemy.org/)
[![JWT](https://img.shields.io/badge/JWT-000000?logo=jsonwebtokens)](https://jwt.io/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Серверная часть (API) для системы управления проектами и задачами. Построена на **FastAPI** + **SQLAlchemy** (асинхронно) + **MySQL**. Предоставляет полноценный RESTful API с JWT-аутентификацией, управлением проектами, задачами и **приглашениями**. Готова к интеграции с любым фронтендом.

---

## 📋 Содержание

- [Основные возможности](#-основные-возможности)
- [Технологический стек](#-технологический-стек)
- [Установка и запуск](#-установка-и-запуск)
- [Переменные окружения](#-переменные-окружения)
- [Миграции базы данных](#-миграции-базы-данных)
- [API Документация](#-api-документация)
  - [Аутентификация](#-аутентификация)
  - [Проекты](#-проекты)
  - [Задачи](#-задачи)
  - [Приглашения](#-приглашения)
- [Инструкция для фронтенда](#-инструкция-для-фронтенда)
- [Структура проекта](#-структура-проекта)
- [Планы по доработке](#-планы-по-доработке)
- [Лицензия](#-лицензия)

---

## 🚀 Основные возможности

- ✅ Регистрация / вход с выдачей **JWT‑токена** (действует 30 мин).
- ✅ Создание, просмотр, обновление, удаление **проектов** (только админ проекта).
- ✅ Управление **участниками** проекта (добавление/удаление – только админ).
- ✅ Создание, просмотр, обновление, удаление **задач** внутри проекта.
- ✅ Назначение задач пользователям, изменение статуса (`pending`, `in_progress`, `completed`).
- ✅ Получение задач, назначенных текущему пользователю.
- ✅ **Приглашения в проекты** – админ отправляет приглашение, пользователь принимает/отклоняет, после принятия автоматически добавляется в проект.
- ✅ Полная документация OpenAPI (Swagger UI) – доступна по `/docs`.
- ✅ Глобальная обработка ошибок с понятными HTTP‑статусами.
- ✅ Декоратор для логирования вызовов функций (вспомогательный).

---

## 🛠 Технологический стек

| Технология | Назначение |
|------------|------------|
| **Python 3.11+** | Язык программирования |
| **FastAPI** | Веб‑фреймворк (асинхронный) |
| **SQLAlchemy** | ORM (асинхронный режим) |
| **MySQL** | Реляционная база данных |
| **aiomysql** | Асинхронный драйвер для MySQL |
| **Alembic** | Управление миграциями схемы БД |
| **python‑jose** | Работа с JWT (создание, верификация) |
| **bcrypt** | Хеширование паролей |
| **Pydantic** | Валидация данных и настройки |
| **Uvicorn** | ASGI‑сервер для разработки |

---

## ⚙️ Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/task-to-do-backend.git
cd task-to-do-backend
```

### 2. Виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
# или
venv\Scripts\activate         # Windows
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```
Если `requirements.txt` нет, создайте его со следующим содержимым:
```txt
fastapi
uvicorn[standard]
sqlalchemy
aiomysql
alembic
python-jose[cryptography]
bcrypt
pydantic-settings
python-dotenv
```

### 4. База данных MySQL
Убедитесь, что MySQL запущен, и создайте базу данных:
```sql
CREATE DATABASE task_to_do CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
> **💡 Примечание:** Таблицы можно создать через Alembic (см. раздел [Миграции](#-миграции-базы-данных)) или вручную по моделям.

### 5. Настройка переменных окружения
Скопируйте `.env.example` в `.env` и заполните своими данными (см. раздел ниже).

### 6. Применение миграций (если нужно)
```bash
alembic upgrade head
```
> Если таблицы уже созданы вручную, этот шаг можно пропустить.

### 7. Запуск сервера
```bash
uvicorn main:app --reload
```
Сервер будет доступен по адресу `http://localhost:8000`  
Документация API – `http://localhost:8000/docs`

---

## 🔐 Переменные окружения (файл `.env`)

```env
# База данных
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=task_to_do
DB_DRIVER=aiomysql

# JWT
JWT_SECRET_KEY=your_secret_key_here   # сгенерируйте надёжный ключ
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (для продакшена укажите конкретные домены)
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

> ⚠️ **Важно:** `JWT_SECRET_KEY` должен быть задан обязательно. Никогда не загружайте `.env` в публичный репозиторий.

---

## 🗄️ Миграции базы данных

Alembic уже настроен. Команды:

| Действие | Команда |
|----------|---------|
| Создать миграцию (автоматически) | `alembic revision --autogenerate -m "описание"` |
| Применить все миграции | `alembic upgrade head` |
| Откат на одну версию назад | `alembic downgrade -1` |

> **Текущее состояние:** В репозитории есть конфигурация Alembic и пустая миграция. Таблицы уже созданы вручную, все будущие изменения рекомендуется проводить через Alembic.

---

## 📚 API Документация

Все эндпоинты имеют префикс `/api/v1`.  
Интерактивная документация доступна по адресам `/docs` (Swagger UI) и `/redoc`.

Ниже приведены основные эндпоинты с примерами.

---

### 🔐 Аутентификация

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST  | `/auth/register` | Регистрация нового пользователя |
| POST  | `/auth/login`    | Вход, получение токена |
| GET   | `/auth/me`       | Информация о текущем пользователе |

#### Регистрация
```json
POST /api/v1/auth/register
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password"
}
```
**Ответ (201):**
```json
{ "message": "Пользователь создан" }
```

#### Логин
```json
POST /api/v1/auth/login
{
  "username_or_email": "john_doe",
  "password": "secure_password"
}
```
**Ответ (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Профиль
`GET /api/v1/auth/me`  
Заголовок: `Authorization: Bearer <token>`
**Ответ:**
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

Все эндпоинты требуют аутентификации.

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET    | `/projects` | Проекты, где пользователь – админ |
| GET    | `/projects/all` | Все проекты пользователя (включая членство) |
| POST   | `/projects` | Создать проект |
| GET    | `/projects/{project_id}` | Информация о проекте + участники |
| PUT    | `/projects/{project_id}` | Обновить название/описание (только админ) |
| DELETE | `/projects/{project_id}` | Удалить проект (только админ) |
| POST   | `/projects/{project_id}/members` | Добавить участника (только админ) |
| DELETE | `/projects/{project_id}/members` | Удалить участника (только админ) |

#### Создание проекта
```json
POST /api/v1/projects
{
  "project_name": "Новый проект",
  "project_description": "Описание"
}
```

#### Получение проекта
`GET /api/v1/projects/1`
**Ответ:**
```json
{
  "project_id": 1,
  "project_name": "Новый проект",
  "project_description": "Описание",
  "admin_id": 1,
  "members": [ { "user_id": 1, "username": "john_doe", "email": "john@example.com", "created_date": "..." } ]
}
```

#### Добавление участника
```json
POST /api/v1/projects/1/members
{ "user_id": 2 }
```
**Ответ:** `{ "message": "Пользователь добавлен в проект!" }`

---

### ✅ Задачи

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET    | `/projects/{project_id}/tasks` | Все задачи проекта |
| POST   | `/projects/{project_id}/tasks` | Создать задачу |
| GET    | `/projects/{project_id}/tasks/{task_id}` | Детали задачи |
| PUT    | `/projects/{project_id}/tasks/{task_id}` | Обновить задачу (любой участник) |
| PATCH  | `/projects/{project_id}/tasks/{task_id}/status` | Изменить статус |
| DELETE | `/projects/{project_id}/tasks/{task_id}` | Удалить (только админ) |
| GET    | `/tasks` | Задачи, назначенные текущему пользователю |

#### Создание задачи
```json
POST /api/v1/projects/1/tasks
{
  "title": "Написать документацию",
  "task_description": "Описание",
  "task_status": "pending",
  "assigned_to": 2,
  "deadline": "2026-09-01"
}
```

#### Изменение статуса
```json
PATCH /api/v1/projects/1/tasks/1/status
{ "task_status": "completed" }
```
**Ответ:** `{ "message": "Статус обновлен!" }`

---

### 📨 Приглашения

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST   | `/projects/{project_id}/invitations` | Отправить приглашение (только админ) |
| GET    | `/invitations` | Приглашения для текущего пользователя (pending) |
| GET    | `/invitations/project/{project_id}` | Приглашения проекта (только админ) |
| PATCH  | `/invitations/{invitation_id}` | Принять / отклонить (только получатель) |
| DELETE | `/invitations/{invitation_id}` | Отменить приглашение (админ или отправитель) |

#### Отправка приглашения
```json
POST /api/v1/projects/1/invitations
{
  "user_id": 3,
  "message": "Присоединяйтесь!"
}
```

#### Ответ на приглашение
```json
PATCH /api/v1/invitations/5
{ "action": "accepted" }   // или "declined"
```
**Ответ:** `{ "message": "Приглашение accepted" }`

#### Отмена приглашения
`DELETE /api/v1/invitations/5` → `{ "message": "Приглашение отменено" }`

---

## 🖥️ Инструкция для фронтенда

### 1. Базовый URL
`http://localhost:8000/api/v1` (в продакшене – ваш домен).

### 2. Аутентификация
- После логина сохраняйте `access_token`.
- Отправляйте его в заголовке: `Authorization: Bearer <token>`.
- Токен истекает через **30 минут**. При необходимости реализуйте автоматический повторный вход.

### 3. Форматы данных
- Даты: `YYYY-MM-DD` (для дат), `YYYY-MM-DDTHH:MM:SS` (для datetime).
- Enum‑поля:
  - `task_status`: `"pending"`, `"in_progress"`, `"completed"`
  - `role_project`: `"admin"`, `"member"`
  - `status_invited`: `"pending"`, `"accepted"`, `"declined"`

### 4. Обработка ошибок
Все ошибки возвращаются в формате:
```json
{ "detail": "Текст ошибки" }
```
Коды статусов:
- `200` – успех
- `201` – создано
- `400` – плохой запрос
- `401` – не авторизован
- `403` – доступ запрещён
- `404` – не найдено
- `409` – конфликт (дубликат и т.п.)
- `422` – ошибка валидации

### 5. CORS
Для разработки разрешены все источники. Для продакшена укажите `CORS_ORIGINS` в `.env` через запятую.

### 6. Пример на JavaScript
```javascript
const login = async (usernameOrEmail, password) => {
  const res = await fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username_or_email: usernameOrEmail, password })
  });
  const data = await res.json();
  localStorage.setItem('token', data.access_token);
};

const getProjects = async () => {
  const token = localStorage.getItem('token');
  const res = await fetch('http://localhost:8000/api/v1/projects', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return res.json();
};
```

---

## 🧱 Структура проекта

```
task-to-do-backend/
├── alembic/                     # Миграции Alembic
│   ├── versions/                # Файлы миграций (пока пусто)
│   ├── env.py
│   └── script.py.mako
├── api/
│   └── v1/
│       ├── auth.py              # Роутеры аутентификации
│       ├── projects.py          # Роутеры проектов
│       ├── tasks.py             # Роутеры задач
│       └── invitations.py       # Роутеры приглашений
├── core/
│   ├── config.py                # Настройки (pydantic-settings)
│   ├── database.py              # Подключение к БД (async engine, session)
│   ├── dependencies.py          # Зависимости (БД, текущий пользователь)
│   ├── exceptions.py            # Кастомные исключения и обработчики
│   └── security.py              # Хеширование, JWT
├── models/                      # SQLAlchemy модели
│   ├── user.py
│   ├── project.py
│   ├── task.py
│   ├── project_members.py
│   └── project_invitations.py
├── repositories/                # Слой доступа к данным
│   ├── base.py
│   ├── user_repository.py
│   ├── project_repository.py
│   ├── task_repository.py
│   └── project_invitation_repository.py
├── schemas/                     # Pydantic схемы
│   ├── auth.py
│   ├── user.py
│   ├── project.py
│   ├── task.py
│   ├── common.py
│   └── invitation.py
├── services/                    # Бизнес-логика
│   ├── auth_service.py
│   ├── project_service.py
│   ├── task_service.py
│   ├── user_service.py
│   └── invitation_service.py
├── utils/                       # Вспомогательные утилиты
│   ├── decorators.py            # Декоратор для логирования вызовов
│   └── logger_setup.py          # (в разработке) настройка логирования
├── .env                         # Переменные окружения (не в репозитории)
├── .env.example                 # Шаблон .env
├── alembic.ini                  # Конфигурация Alembic
├── main.py                      # Точка входа FastAPI
└── requirements.txt             # Зависимости Python
```

---

## 📌 Планы по доработке

- [x] **Приглашения в проекты** – полностью реализовано.
- [ ] **Чат проекта** – обмен сообщениями между участниками.
- [ ] **Уведомления** – оповещения о событиях (приглашения, изменения задач).
- [ ] **Фильтрация задач** – по статусу, проекту, датам и т.д.
- [ ] **Процент готовности проекта** – расчёт завершённости.
- [ ] **Контейнеризация** – Dockerfile + docker-compose для быстрого запуска.
- [ ] **Юнит-тесты** – pytest + httpx.
- [ ] **Логирование** – запись в файл/ELK (сейчас есть декоратор, требуется полноценная настройка).

---

## 📄 Лицензия

Этот проект является учебным и распространяется под лицензией MIT (или укажите свою).

---

**💬 Связь:** Если у вас возникли вопросы или предложения, создавайте issue в репозитории.

---

*Обновлено: август 2026*
```
