// HTTP-клиент для FastAPI. Адрес можно переопределить в api-config.js.
const API_BASE = String(window.TASKER_API_BASE || `${window.location.protocol}//${window.location.hostname}:8000/api/v1`).replace(/\/+$/, "");
const TOKEN_KEY = "tasker_access_token";
let sessionGeneration = 0;
const pendingRequests = new Set();
function invalidateRequests() {
    sessionGeneration++;
    for (const controller of pendingRequests) controller.abort();
    pendingRequests.clear();
}
function getToken() { return localStorage.getItem(TOKEN_KEY); }
function setToken(token) { invalidateRequests(); localStorage.setItem(TOKEN_KEY, token); }
function clearToken() { invalidateRequests(); localStorage.removeItem(TOKEN_KEY); }
function assertSession(generation) {
    if (generation !== sessionGeneration) throw new DOMException("Сессия изменена", "AbortError");
}

async function api(method, path, body = undefined) {
    const generation = sessionGeneration;
    const controller = new AbortController();
    const token = getToken();
    const publicAuth = path.startsWith("/auth/");
    const options = { method, headers: { Accept: "application/json" }, signal: controller.signal };
    if (token && !publicAuth) options.headers.Authorization = `Bearer ${token}`;
    if (body !== undefined) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);
    }
    pendingRequests.add(controller);
    const timer = setTimeout(() => controller.abort(), 15000);
    try {
        const response = await fetch(`${API_BASE}${path}`, options);
        assertSession(generation);
        const content = await response.text();
        assertSession(generation);
        let data = null;
        if (content) {
            try { data = JSON.parse(content); }
            catch { if (response.ok) throw new Error("Сервер вернул некорректный JSON"); }
        }
        if (!response.ok) {
            const detail = Array.isArray(data?.detail)
                ? data.detail.map(item => item?.msg || String(item)).join("; ")
                : data?.detail;
            const error = new Error(typeof detail === "string" && detail ? detail : `Ошибка HTTP ${response.status}`);
            error.status = response.status;
            if (response.status === 401 && token && !publicAuth) {
                // Обработчик выхода инвалидирует запросы, токен и состояние.
                window.dispatchEvent(new Event("tasker:unauthorized"));
            }
            throw error;
        }
        return data;
    } catch (error) {
        if (generation !== sessionGeneration) {
            if (error.status === 401) throw error;
            throw new DOMException("Сессия изменена", "AbortError");
        }
        if (error.name === "AbortError") throw new Error("Превышено время ожидания сервера. Если операция изменяла данные, проверьте результат перед повтором.");
        if (error instanceof TypeError) throw new Error("Не удалось связаться с сервером");
        throw error;
    } finally {
        clearTimeout(timer);
        pendingRequests.delete(controller);
    }
}

// FastAPI допускает максимум 100 записей на страницу.
async function apiAll(path) {
    const generation = sessionGeneration;
    const items = [];
    const url = new URL(path, "http://tasker.local");
    url.searchParams.set("size", "100");
    for (let page = 1; ; page++) {
        url.searchParams.set("page", String(page));
        const result = await api("GET", url.pathname + url.search);
        assertSession(generation);
        if (!Array.isArray(result?.items) || !Number.isInteger(result.pages) || result.pages < 0) {
            throw new Error("Некорректный ответ пагинации");
        }
        items.push(...result.items);
        if (page >= result.pages) return items;
        if (!result.items.length) throw new Error("Сервер вернул пустую промежуточную страницу");
    }
}

// Единая блокировка одинаковых операций, независимо от количества кнопок.
const pendingWrites = new Set();
async function withWriteLock(resource, operation) {
    const generation = sessionGeneration;
    const key = `${generation}:${resource}`;
    if (pendingWrites.has(key)) return false;
    pendingWrites.add(key);
    try { return await operation(generation); }
    finally { pendingWrites.delete(key); }
}
