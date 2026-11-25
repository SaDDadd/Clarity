// Файл для работы с задачами (создание, обновление, удаление, смена статуса)

// Проверка, может ли пользователь управлять задачей (админ или куратор)
function canManageTask(task) {
    return canManageProject(getProject(task?.projectId));
}

// Проверка, может ли пользователь менять статус задачи
function canChangeTaskStatus(task) {
    const project = getProject(task?.projectId);
    return Boolean(
        project &&
        (canManageProject(project) || Number(task.assigneeId) === Number(currentUser?.id))
    );
}

// Создание новой задачи
async function createTask(data) {
    const project = getProject(data.projectId);
    if (!project || !canManageProject(project)) {
        showToast("Только администратор проекта или куратор могут создавать задачи");
        return false;
    }

    const result = await api("POST", `/projects/${Number(data.projectId)}/tasks`, mapTaskToServer(data));
    const task = mapTaskFromServer(result);

    if (Number.isInteger(task.id)) {
        tasks.push(task);
        await loadProjectDetails(task.projectId);
    }

    currentProjectId = Number(data.projectId);
    currentPage = "overview";
    saveSettings();
    render();
    showToast("✓ Задача создана");
    return true;
}

// Обновление существующей задачи
async function updateTask(taskId, data) {
    const task = tasks.find(item => Number(item.id) === Number(taskId));
    if (!task || !canManageTask(task)) {
        showToast("Только администратор или куратор могут редактировать параметры задачи");
        return false;
    }

    const project = getProject(data.projectId);
    if (!project || !canManageProject(project)) return false;

    await api("PUT", `/projects/${Number(data.projectId)}/tasks/${Number(taskId)}`, mapTaskToServer(data));

    await loadProjectDetails(data.projectId);
    showToast("✓ Изменения сохранены");
    return true;
}

// Удаление задачи
async function deleteTask(taskId) {
    const task = tasks.find(item => Number(item.id) === Number(taskId));
    if (!task || !canManageTask(task)) {
        showToast("Только администратор может удалить задачу");
        return false;
    }
    if (!confirm(`Удалить задачу "${task.title}"?`)) return false;

    await api("DELETE", `/projects/${Number(task.projectId)}/tasks/${Number(task.id)}`);
    tasks = tasks.filter(item => Number(item.id) !== Number(task.id));
    projectTaskCache.set(Number(task.projectId), getProjectTasks(task.projectId));
    closeTaskModal();
    closeTaskMenu();
    render();
    showToast("✓ Задача удалена");
    return true;
}

// Изменение статуса задачи
async function changeTaskStatus(taskId, status) {
    const task = tasks.find(item => Number(item.id) === Number(taskId));
    if (!task || !STATUS[status]) return false;
    if (!canChangeTaskStatus(task)) {
        showToast("Статус может менять администратор или назначенный исполнитель");
        return false;
    }

    await api(
        "PATCH",
        `/projects/${Number(task.projectId)}/tasks/${Number(task.id)}/status`,
        { task_status: statusToBackend[status] }
    );

    task.status = status;
    closeTaskMenu();
    render();
    showToast(`✓ Статус: ${STATUS[status]}`);
    return true;
}

// Добавление/удаление задачи из избранного
async function toggleFavorite(taskId) {
    const task = tasks.find(item => Number(item.id) === Number(taskId));
    if (!task || !canManageTask(task)) {
        showToast("Избранное для задачи могут изменить только администратор или куратор проекта");
        return false;
    }

    const payload = {
        title: task.title,
        description: task.description,
        projectId: task.projectId,
        assigneeId: task.assigneeId,
        status: task.status,
        priority: task.priority,
        date: task.date,
        favorite: !task.favorite
    };

    await api(
        "PUT",
        `/projects/${Number(task.projectId)}/tasks/${Number(task.id)}`,
        mapTaskToServer(payload)
    );

    await loadProjectDetails(task.projectId);

    closeTaskMenu();
    showToast(task.favorite ? "✓ Добавлено в избранное" : "Удалено из избранного");
    return true;
}