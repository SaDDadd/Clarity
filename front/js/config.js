const STORAGE = {
    settings: "tasker_settings",
    currentProject: "tasker_current_project",
    currentPage: "tasker_current_page",
    currentView: "tasker_current_view"
};

const STATUS = {
    todo: "К выполнению",
    progress: "В работе",
    done: "Готово"
};

const statusFromBackend = {
    pending: "todo",
    in_progress: "progress",
    completed: "done"
};

const statusToBackend = {
    todo: "pending",
    progress: "in_progress",
    done: "completed"
};

const PRIORITY = {
    high: "Высокий",
    medium: "Средний",
    low: "Низкий"
};

const DEFAULT_SETTINGS = {
    theme: "light",
    sort: "newest"
};

const DEFAULT_USER = {
    id: null,
    name: "Пользователь",
    nickname: "Пользователь",
    email: "",
    createdAt: null
};