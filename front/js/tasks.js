// Файл для работы с задачами (создание, обновление, удаление, смена статуса)

// Проверка, может ли пользователь управлять задачей (админ или куратор)
function canManageTask(task) {
    return canManageProject(getProject(task?.projectId));
}

// Проверка, может ли пользователь менять статус задачи
function canChangeTaskStatus(task) {
    return canEditTask(task);
}

function isTaskPerformer(task) {
    return Boolean(task && currentUser?.id != null && task.assigneeId != null &&
        Number(task.assigneeId) === Number(currentUser.id) && getProject(task.projectId));
}

function canEditTask(task) {
    return canManageTask(task) || isTaskPerformer(task);
}

function canToggleFavorite(task) {
    return canEditTask(task);
}

function validateTaskData(data) {
    const title = String(data.title || "").trim();
    if (!title || title.length > 150) throw new Error("Название задачи: от 1 до 150 символов");
    if (String(data.description || "").trim().length > 1000) throw new Error("Описание задачи: не более 1000 символов");
    if (!Object.hasOwn(STATUS, data.status) || !Object.hasOwn(PRIORITY, data.priority)) throw new Error("Некорректный статус или приоритет");
}
function syncTaskCache(projectId) {
    invalidateProjectReads(projectId);
    projectTaskCache.set(Number(projectId), getProjectTasks(projectId));
}
async function createTask(data) {
    const project = getProject(data.projectId);
    if (!canManageProject(project)) { showToast("Только администратор или куратор могут создавать задачи"); return false; }
    validateTaskData(data);
    if (data.date && data.date < getTodayISO()) throw new Error("Дедлайн не может быть в прошлом");
    if (data.assigneeId != null && !getProjectAccounts(project.id).some(account => account.id === Number(data.assigneeId))) throw new Error("Исполнитель не входит в проект");
    return withWriteLock(`task:create:${project.id}`, async generation => {
        const result = await api("POST", `/projects/${project.id}/tasks`, mapTaskToServer(data));
        assertSession(generation);
        const task = mapTaskFromServer(result);
        if (Number.isInteger(task.id) && task.id > 0) {
            tasks = tasks.filter(item => item.id !== task.id); tasks.push(task); syncTaskCache(project.id);
        } else { invalidateProjectReads(project.id); showToast("Задача создана, обновите данные для отображения"); return true; }
        currentProjectId = project.id; currentPage = "overview"; saveSettings(); render();
        showToast("✓ Задача создана"); return true;
    });
}

async function updateTask(taskId, data) {
    const task = tasks.find(item => item.id === Number(taskId));
    if (!canEditTask(task)) { showToast("Недостаточно прав для изменения задачи"); return false; }
    if (Number(data.projectId) !== task.projectId) throw new Error("Перенос задачи в другой проект не поддерживается");
    validateTaskData(data);
    const before = mapTaskToServer(task), after = mapTaskToServer(data);
    const allowed = ["title", "task_description", "task_status", "task_favorite"];
    if (canManageTask(task)) allowed.push("deadline", "assigned_to", "task_priority");
    const patch = Object.fromEntries(allowed.filter(key => before[key] !== after[key]).map(key => [key, after[key]]));
    if (patch.deadline && patch.deadline < getTodayISO()) throw new Error("Дедлайн не может быть в прошлом");
    if (patch.assigned_to != null && !getProjectAccounts(task.projectId).some(account => account.id === patch.assigned_to)) throw new Error("Исполнитель не входит в проект");
    if (!Object.keys(patch).length) { showToast("Нет изменений"); return true; }
    return withWriteLock(`task:${task.id}`, async generation => {
        await api("PUT", `/projects/${task.projectId}/tasks/${task.id}`, patch);
        assertSession(generation);
        const live = tasks.find(item => item.id === task.id);
        if (live) {
            const updated = mapTaskFromServer({ ...mapTaskToServer(live), ...patch, task_id: live.id, project_id: live.projectId, created_date: live.createdAt, update_date: new Date().toISOString() });
            Object.assign(live, updated);
        }
        syncTaskCache(task.projectId); render(); showToast("✓ Изменения сохранены"); return true;
    });
}

async function deleteTask(taskId) {
    const task = tasks.find(item => item.id === Number(taskId));
    if (!canManageTask(task)) { showToast("Только администратор или куратор может удалить задачу"); return false; }
    return withWriteLock(`task:${task.id}`, async generation => {
        if (!confirm(`Удалить задачу "${task.title}"?`)) return false;
        await api("DELETE", `/projects/${task.projectId}/tasks/${task.id}`);
        assertSession(generation);
        tasks = tasks.filter(item => item.id !== task.id); syncTaskCache(task.projectId);
        if (Number(elements.taskForm.dataset.editingId) === task.id) closeTaskModal();
        closeTaskMenu(); render(); showToast("✓ Задача удалена"); return true;
    });
}

async function changeTaskStatus(taskId, status) {
    const task = tasks.find(item => item.id === Number(taskId));
    if (!task || !Object.hasOwn(STATUS, status)) return false;
    if (!canChangeTaskStatus(task)) { showToast("Статус может менять администратор, куратор или назначенный исполнитель"); return false; }
    if (task.status === status) return true;
    return withWriteLock(`task:${task.id}`, async generation => {
        await api("PATCH", `/projects/${task.projectId}/tasks/${task.id}/status`, { task_status: statusToBackend[status] });
        assertSession(generation);
        const live = tasks.find(item => item.id === task.id);
        if (live) { live.status = status; live.updatedAt = new Date().toISOString(); }
        syncTaskCache(task.projectId); closeTaskMenu(); render(); showToast(`✓ Статус: ${STATUS[status]}`); return true;
    });
}

async function toggleFavorite(taskId) {
    const task = tasks.find(item => item.id === Number(taskId));
    if (!canToggleFavorite(task)) { showToast("Недостаточно прав для изменения избранного"); return false; }
    return withWriteLock(`task:${task.id}`, async generation => {
        const nextFavorite = !task.favorite;
        await api("PUT", `/projects/${task.projectId}/tasks/${task.id}`, { task_favorite: nextFavorite });
        assertSession(generation);
        const live = tasks.find(item => item.id === task.id);
        if (live) { live.favorite = nextFavorite; live.updatedAt = new Date().toISOString(); }
        syncTaskCache(task.projectId); closeTaskMenu(); render();
        showToast(nextFavorite ? "✓ Добавлено в избранное" : "Удалено из избранного"); return true;
    });
}
