// Файл для работы с данными пользователей (кэширование, поиск)

// Получение никнейма по ID из кэша
function getNicknameById(userId) {
    const id = Number(userId);
    if (!id) return "Не назначен";
    if (id === Number(currentUser?.id)) return currentUser.nickname || currentUser.name || "Пользователь";
    return userCache.get(id) || `Пользователь #${id}`;
}

// Асинхронная загрузка и кэширование имени пользователя
const pendingUsers = new Map();
async function ensureUserCached(userId) {
    const id = Number(userId);
    if (!id || userCache.has(id)) return userCache.get(id) || null;
    const key = `${sessionGeneration}:${id}`;
    if (pendingUsers.has(key)) return pendingUsers.get(key);
    const generation = sessionGeneration;
    const request = (async () => {
        try {
            const found = await api("GET", `/users/${id}`);
            const name = cleanNickname(found?.username);
            if (generation === sessionGeneration && name) userCache.set(id, name);
            return generation === sessionGeneration ? name || null : null;
        } catch { return null; }
        finally { pendingUsers.delete(key); }
    })();
    pendingUsers.set(key, request);
    return request;
}

// Поиск пользователей по никнейму
async function searchUsers(query) {
    const normalized = cleanNickname(query);
    if (normalized.length < 2) return [];
    const result = await api("GET", `/users/search?search_user=${encodeURIComponent(normalized)}`);
    // Бэкенд FastAPI возвращает объект с массивом в items
    const list = Array.isArray(result) ? result : (Array.isArray(result?.items) ? result.items : []);
    return list.map(item => ({
        id: Number(item?.user_id ?? item?.id),
        username: cleanNickname(item?.username || item?.nickname || item?.name),
        email: String(item?.email || "")
    })).filter(item => item.id && item.username);
}