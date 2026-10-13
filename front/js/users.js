function getNicknameById(userId) {
    const id = Number(userId);
    if (!id) return "Не назначен";
    if (id === Number(currentUser?.id)) return currentUser.nickname || currentUser.name || "Пользователь";
    return userCache.get(id) || `Пользователь #${id}`;
}

async function ensureUserCached(userId) {
    const id = Number(userId);
    if (!id || userCache.has(id)) return userCache.get(id) || null;
    try {
        const result = await api("GET", `/users/search?search_user=${encodeURIComponent(String(id))}`);
        const list = Array.isArray(result) ? result : [];
        const found = list.find(item => Number(item?.user_id ?? item?.id) === id) || list[0];
        if (found) {
            const name = cleanNickname(found.username || found.nickname || found.name);
            if (name) userCache.set(Number(found.user_id ?? found.id), name);
        }
    } catch {
        return null;
    }
    return userCache.get(id) || null;
}

async function searchUsers(query) {
    const normalized = cleanNickname(query);
    if (normalized.length < 2) return [];
    const result = await api("GET", `/users/search?search_user=${encodeURIComponent(normalized)}`);
    const list = Array.isArray(result) ? result : [];
    return list.map(item => ({
        id: Number(item?.user_id ?? item?.id),
        username: cleanNickname(item?.username || item?.nickname || item?.name),
        email: String(item?.email || "")
    })).filter(item => item.id && item.username);
}