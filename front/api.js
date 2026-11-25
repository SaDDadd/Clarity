// Файл для настройки и выполнения HTTP-запросов к бэкенду

// Базовый URL для всех запросов к API
const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000/api/v1`;
// Ключ для хранения токена авторизации в localStorage
const TOKEN_KEY = "tasker_access_token";

// Получение токена из хранилища
function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

// Сохранение токена в хранилище
function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

// Удаление токена из хранилища
function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
}

// Основная функция для выполнения запросов к API
async function api(method, path, body = undefined) {
    const options = {
        method,
        headers: {
            Accept: "application/json"
        }
    };

    const token = getToken();
    if (token) options.headers.Authorization = `Bearer ${token}`;

    if (body !== undefined) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE}${path}`, options);
    let data = null;

    // Парсинг ответа от сервера
    try {
        data = await response.json();
    } catch {
        data = null;
    }

    // Обработка ошибочных статусов HTTP
    if (!response.ok) {
        // При 401 ошибке очищаем токен и оповещаем приложение
        if (response.status === 401) {
            clearToken();
            window.dispatchEvent(new Event("tasker:unauthorized"));
        }

        let message;
        // Бэкенд FastAPI возвращает массив ошибок валидации в поле detail
        if (Array.isArray(data?.detail)){
            message = data.detail.map(item => item?.msg || String(item)).join("; ");
        } 
        else{
            message = data?.detail;
        }
        throw new Error(message || `Ошибка HTTP ${response.status}`);
    }

    return data;
}