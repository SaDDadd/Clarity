// Файл для работы с проектами (права, загрузка, создание, удаление)

// Получение проекта из массива без проверки прав
function getProjectRaw(projectId) {
    const id = Number(projectId);
    return projects.find(project => Number(project.id) === id) || null;
}

// Проверка, является ли пользователь администратором проекта
function isProjectAdmin(project, userId = currentUser?.id) {
    return Boolean(project && userId != null && Number(project.adminId) === Number(userId));
}

// Проверка, может ли пользователь управлять проектом (админ или куратор)
function canManageProject(project) {
    if (!project) return false;
    if (project.role == "admin" || project.role == "curator") return true;
    return isProjectAdmin(project);
}

// Проверка, является ли пользователь участником проекта
function isProjectMember(project, userId = currentUser?.id) {
    return Boolean(
        project &&
        userId != null &&
        Array.isArray(project.memberIds) &&
        project.memberIds.some(id => Number(id) === Number(userId))
    );
}

// Проверка доступа к проекту
function canAccessProject(project, userId = currentUser?.id) {
    return isProjectAdmin(project, userId) || isProjectMember(project, userId);
}

// Получение списка доступных проектов
function getAccessibleProjects() {
    return projects.filter(project => canAccessProject(project));
}

// Получение списка проектов, которыми можно управлять
function getAdminProjects() {
    return projects.filter(project => canManageProject(project));
}

// Получение проекта, если есть доступ
function getProject(projectId) {
    const project = getProjectRaw(projectId);
    return project && canAccessProject(project) ? project : null;
}

// Получение списка аккаунтов участников проекта
function getProjectAccounts(projectId) {
    const project = getProject(projectId);
    if (!project) return [];
    const members = Array.isArray(project.members) ? project.members : [];
    const ids = [project.adminId, ...(project.memberIds || [])].filter(id => Number.isInteger(Number(id)));
    const result = [];
    const seen = new Set();

    ids.forEach(id => {
        const numberId = Number(id);
        if (seen.has(numberId)) return;
        seen.add(numberId);
        const member = members.find(item => Number(item?.user_id ?? item?.id) === numberId);
        const nickname = userCache.get(numberId) || cleanNickname(member?.username || member?.nickname || member?.name);
        const email = String(member?.email || "");

        let role = member?.role;
        if (!role){
            role = numberId === Number(project.adminId)? "admin" : "member";
        }
        result.push({
            id: numberId,
            nickname: nickname || `Пользователь #${numberId}`,
            name: nickname || `Пользователь #${numberId}`,
            email,
            role
        });
    });
    return result;
}

// Получение текущего выбранного проекта
function getCurrentProject() {
    return getProject(currentProjectId);
}

// Получение задач текущего проекта
function getProjectTasks(projectId = currentProjectId) {
    const id = Number(projectId);
    if (!getProject(id)) return [];
    return tasks.filter(task => Number(task.projectId) === id);
}

// Получение названия проекта по ID
function getProjectName(projectId) {
    return getProject(projectId)?.name || "Без проекта";
}

// Загрузка всех проектов и задач с сервера
async function loadWorkspaceFromServer() {
    const [projectResult, assignedResult] = await Promise.all([
        api("GET", "/projects/all?size=100"),
        api("GET", "/tasks?size=100")
    ]);

    // Бэкенд FastAPI возвращает объект с массивом внутри поля items
    const rawProjects = projectResult?.items || []
    const rawTasks = assignedResult?.items || []


    projects = rawProjects
        .map(mapProjectFromServer)
        .filter(project => Number.isInteger(project.id));

    tasks = rawTasks
        .map(mapTaskFromServer)
        .filter(task => Number.isInteger(task.id));

    projectTaskCache.clear();
    tasks.forEach(task => {
        const id = Number(task.projectId);
        if (!projectTaskCache.has(id)) projectTaskCache.set(id, []);
        projectTaskCache.get(id).push(task);
    });

    validateCurrentProject();
}

// Загрузка деталей конкретного проекта и его задач
async function loadProjectDetails(projectId) {
    const id = Number(projectId);
    const [detailsResult, taskResult] = await Promise.all([
        api("GET", `/projects/${id}`),
        api("GET", `/projects/${id}/tasks?size=100`)
    ]);

    const mappedProject = mapProjectFromServer(detailsResult);
    const index = projects.findIndex(project => Number(project.id) === id);
    if (index >= 0) projects[index] = mappedProject;
    else projects.push(mappedProject);

    // Бэкенд FastAPI возвращает объект с массивом внутри поля items
    const rawTasks = taskResult?.items || [];
    const mappedTasks = rawTasks.map(mapTaskFromServer).filter(task => Number(task.projectId) == id);

    projectTaskCache.set(id, mappedTasks);
    tasks = tasks.filter(task => Number(task.projectId) !== id);
    tasks.push(...mappedTasks);

    currentProjectDetails = mappedProject;
    mappedTasks.forEach(task => {
        if (task.assigneeId) ensureUserCached(task.assigneeId);
    });

    renderProjectMembers(id);
    render();
}

// Создание нового проекта
async function createProject(name, description) {
    if (!currentUser) return false;
    const result = await api("POST", "/projects", {
        project_name: name.trim(),
        project_description: description.trim()
    });
    const project = mapProjectFromServer(result);
    if (!Number.isInteger(project.id)) {
        await loadWorkspaceFromServer();
    } else {
        projects.push(project);
    }
    currentProjectId = project.id || projects.at(-1)?.id || null;
    currentPage = "overview";
    saveSettings();
    render();
    showToast("✓ Проект создан — вы администратор");
    return true;
}

// Обновление информации о проекте
async function updateProject(projectId, name, description) {
    const project = getProject(projectId);
    if (!project || !isProjectAdmin(project)) {
        showToast("Только администратор может изменять проект");
        return false;
    }

    await api("PUT", `/projects/${Number(projectId)}`, {
        project_name: name.trim(),
        project_description: description.trim()
    });

    await loadProjectDetails(projectId);
    showToast("✓ Проект обновлён");
    return true;
}

// Удаление проекта
async function deleteProject(projectId) {
    const project = getProject(projectId);
    if (!project || !isProjectAdmin(project)) {
        showToast("Только администратор может удалить проект");
        return false;
    }

    if (!confirm(`Удалить проект "${project.name}"?`)) return false;

    await api("DELETE", `/projects/${Number(projectId)}`);
    projects = projects.filter(item => Number(item.id) !== Number(projectId));
    tasks = tasks.filter(task => Number(task.projectId) !== Number(projectId));
    projectTaskCache.delete(Number(projectId));

    if (Number(currentProjectId) === Number(projectId)) {
        currentProjectId = getAccessibleProjects()[0]?.id || null;
    }

    closeProjectModal();
    saveSettings();
    render();
    showToast("✓ Проект удалён");
    return true;
}

// Выбор проекта для просмотра
async function selectProject(projectId) {
    const project = getProject(projectId);
    if (!project) return;
    currentProjectId = Number(projectId);
    currentPage = "overview";
    closeAllFloatingMenus();
    saveSettings();
    render();

    try {
        await loadProjectDetails(currentProjectId);
    } catch (error) {
        showToast(getErrorMessage(error));
    }
}

// Добавление участника в проект
async function addProjectMember(projectId, userId) {
    const project = getProject(projectId);
    if (!project || !canManageProject(project)) {
        showToast("Только администратор может добавлять участников");
        return false;
    }

    if (Number(userId) === Number(project.adminId)) {
        showToast("Администратор уже состоит в проекте");
        return false;
    }

    await api("POST", `/projects/${Number(projectId)}/members`, { user_id: Number(userId) });
    await loadProjectDetails(projectId);
    showToast("✓ Участник добавлен в проект");
    return true;
}

// Удаление участника из проекта
async function removeProjectMember(projectId, userId) {
    const project = getProject(projectId);
    if (!project || !canManageProject(project)) return false;
    if (Number(userId) === Number(project.adminId)) return false;

    const nickname = getNicknameById(userId);
    if (!confirm(`Удалить @${nickname} из проекта?`)) return false;

    await api("DELETE", `/projects/${Number(projectId)}/members/${Number(userId)}`);
    await loadProjectDetails(projectId);
    showToast("✓ Участник удалён");
    return true;
}

// Приглашение пользователя в проект
async function inviteProjectMember(projectId, userId) {
    const project = getProject(projectId);
    if (!project || !canManageProject(project)) {
        showToast("Только администратор может приглашать пользователей");
        return false;
    }

    await api("POST", `/projects/${Number(projectId)}/invitations`, {
        user_id: Number(userId),
        message: `Приглашение в проект «${project.name}»`
    });

    showToast("✓ Приглашение отправлено");
    return true;
}