function canManageTask(task) {
    return isProjectAdmin(getProject(task?.projectId));
}

function canChangeTaskStatus(task) {
    const project = getProject(task?.projectId);
    return Boolean(
        project &&
        (isProjectAdmin(project) || Number(task.assigneeId) === Number(currentUser?.id))
    );
}

async function createTask(data) {
    const project = getProject(data.projectId);
    if (!project || !isProjectAdmin(project)) {
        showToast("Только администратор проекта может создавать задачи");
        return false;
    }

    const result = await api("POST", `/projects/${Number(data.projectId)}/tasks`, mapTaskToServer(data));
    const task = mapTaskFromServer(result);

    if (Number.isInteger(task.id)) {
        tasks = tasks.filter(item => Number(item.id) !== Number(task.id));
        tasks.push(task);
        projectTaskCache.set(Number(task.projectId), getProjectTasks(task.projectId));
    }

    currentProjectId = Number(data.projectId);
    currentPage = "overview";
    saveSettings();
    render();
    showToast("✓ Задача создана");
    return true;
}

async function updateTask(taskId, data) {
    const task = tasks.find(item => Number(item.id) === Number(taskId));
    if (!task || !canManageTask(task)) {
        showToast("Только администратор может редактировать параметры задачи");
        return false;
    }

    const project = getProject(data.projectId);
    if (!project || !isProjectAdmin(project)) return false;

    const result = await api(
        "PUT",
        `/projects/${Number(data.projectId)}/tasks/${Number(taskId)}`,
        mapTaskToServer(data)
    );

    const mapped = mapTaskFromServer(result);
    const index = tasks.findIndex(item => Number(item.id) === Number(taskId));
    if (index >= 0) tasks[index] = mapped;
    else tasks.push(mapped);

    await loadProjectDetails(data.projectId);
    showToast("✓ Изменения сохранены");
    return true;
}

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

async function toggleFavorite(taskId) {
    const task = tasks.find(item => Number(item.id) === Number(taskId));
    if (!task || !canManageTask(task)) {
        showToast("Избранное для задачи может изменить только администратор проекта");
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

    task.favorite = !task.favorite;

    closeTaskMenu();
    render();
    showToast(task.favorite ? "✓ Добавлено в избранное" : "Удалено из избранного");
    return true;
}