// Файл для работы с данными пользователей (кэширование, поиск)

// Получение никнейма по ID из кэша
function getNicknameById(userId) {
    const id = Number(userId);
    if (!id) return "Не назначен";
    if (id === Number(currentUser?.id)) return currentUser.nickname || currentUser.name || "Пользователь";
    return userCache.get(id) || `Пользователь #${id}`;
}

// Асинхронная загрузка и кэширование имени пользователя
async function ensureUserCached(userId) {
    const id = Number(userId);
    if (!id || userCache.has(id)) return userCache.get(id) || null;
    try {
        const result = await api("GET", `/users/search?search_user=${encodeURIComponent(String(id))}`);
        // Бэкенд FastAPI может вернуть массив или объект с массивом в items
        const list = Array.isArray(result) ? result : (Array.isArray(result?.items) ? result.items : []);
        const found = list.find(item => Number(item?.user_id ?? item?.id) === id);
        if (found) {
            const name = cleanNickname(found.username || found.nickname || found.name);
            if (name) userCache.set(id, name);
        }
    } 
    catch {
        return null;
    }
    return userCache.get(id) || null;
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