// Файл для работы с localStorage (сохранение настроек и сессии)

// Формирование ключа хранилища, привязанного к ID пользователя
function userStorageKey(baseKey) {
    return currentUser?.id ? `${baseKey}::${currentUser.id}` : baseKey;
}

// Загрузка настроек из localStorage
function loadSettings() {
    try {
        const raw = localStorage.getItem(userStorageKey(STORAGE.settings));
        return raw ? { ...DEFAULT_SETTINGS, ...JSON.parse(raw) } : { ...DEFAULT_SETTINGS };
    } catch {
        return { ...DEFAULT_SETTINGS };
    }
}

// Сохранение настроек в localStorage
function saveSettings() {
    if (!currentUser) return;
    localStorage.setItem(userStorageKey(STORAGE.settings), JSON.stringify(settings));
    localStorage.setItem(userStorageKey(STORAGE.currentPage), currentPage);
    localStorage.setItem(userStorageKey(STORAGE.currentView), currentView);
    if (currentProjectId !== null && currentProjectId !== undefined) {
        localStorage.setItem(userStorageKey(STORAGE.currentProject), String(currentProjectId));
    } else {
        localStorage.removeItem(userStorageKey(STORAGE.currentProject));
    }
}

// Очистка локальных данных при выходе из аккаунта
function clearLocalWorkspace() {
    projects = [];
    tasks = [];
    invitations = [];
    projectTaskCache.clear();
    currentProjectDetails = null;
    currentProjectId = null;
    currentPage = "overview";
    currentView = "board";
    userCache.clear();
}