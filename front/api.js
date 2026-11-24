const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000/api/v1`;
const TOKEN_KEY = "tasker_access_token";

function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
}

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

    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        if (response.status === 401) {
            clearToken();
            window.dispatchEvent(new Event("tasker:unauthorized"));
        }

        let message;
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
