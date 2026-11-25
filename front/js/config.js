// Файл с глобальными константами и настройками по умолчанию

// Ключи для хранения данных в localStorage
const STORAGE = {
    settings: "tasker_settings",
    currentProject: "tasker_current_project",
    currentPage: "tasker_current_page",
    currentView: "tasker_current_view"
};

// Статусы задач для отображения в интерфейсе
const STATUS = {
    todo: "К выполнению",
    progress: "В работе",
    done: "Готово"
};

// Маппинг статусов с бэкенда в статусы фронтенда
const statusFromBackend = {
    pending: "todo",
    in_progress: "progress",
    completed: "done"
};

// Маппинг статусов с фронтенда в статусы бэкенда
const statusToBackend = {
    todo: "pending",
    progress: "in_progress",
    done: "completed"
};

// Приоритеты задач
const PRIORITY = {
    high: "Высокий",
    medium: "Средний",
    low: "Низкий"
};

// Роли пользователей в проекте
const ROLE = {
    admin: "Администратор",
    curator: "Куратор",
    member: "Участник"
};

// Настройки приложения по умолчанию
const DEFAULT_SETTINGS = {
    theme: "light",
    sort: "newest"
};

// Данные пользователя по умолчанию
const DEFAULT_USER = {
    id: null,
    name: "Пользователь",
    nickname: "Пользователь",
    email: "",
    createdAt: null
};