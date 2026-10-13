function getProjectRaw(projectId) {
    const id = Number(projectId);
    return projects.find(project => Number(project.id) === id) || null;
}

function isProjectAdmin(project, userId = currentUser?.id) {
    return Boolean(project && userId != null && Number(project.adminId) === Number(userId));
}

function isProjectMember(project, userId = currentUser?.id) {
    return Boolean(
        project &&
        userId != null &&
        Array.isArray(project.memberIds) &&
        project.memberIds.some(id => Number(id) === Number(userId))
    );
}

function canAccessProject(project, userId = currentUser?.id) {
    return isProjectAdmin(project, userId) || isProjectMember(project, userId);
}

function getAccessibleProjects() {
    return projects.filter(project => canAccessProject(project));
}

function getAdminProjects() {
    return projects.filter(project => isProjectAdmin(project));
}

function getProject(projectId) {
    const project = getProjectRaw(projectId);
    return project && canAccessProject(project) ? project : null;
}

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
        result.push({
            id: numberId,
            nickname: nickname || `Пользователь #${numberId}`,
            name: nickname || `Пользователь #${numberId}`,
            email
        });
    });
    return result;
}

function getCurrentProject() {
    return getProject(currentProjectId);
}

function getProjectTasks(projectId = currentProjectId) {
    const id = Number(projectId);
    if (!getProject(id)) return [];
    return tasks.filter(task => Number(task.projectId) === id);
}

function getProjectName(projectId) {
    return getProject(projectId)?.name || "Без проекта";
}

async function loadWorkspaceFromServer() {
    const [projectResult, assignedResult] = await Promise.all([
        api("GET", "/projects/all"),
        api("GET", "/tasks")
    ]);

    projects = (Array.isArray(projectResult) ? projectResult : [])
        .map(mapProjectFromServer)
        .filter(project => Number.isInteger(project.id));

    tasks = (Array.isArray(assignedResult) ? assignedResult : [])
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

async function loadProjectDetails(projectId) {
    const id = Number(projectId);
    const [detailsResult, taskResult] = await Promise.all([
        api("GET", `/projects/${id}`),
        api("GET", `/projects/${id}/tasks`)
    ]);

    const mappedProject = mapProjectFromServer(detailsResult);
    const index = projects.findIndex(project => Number(project.id) === id);
    if (index >= 0) projects[index] = mappedProject;
    else projects.push(mappedProject);

    const mappedTasks = (Array.isArray(taskResult) ? taskResult : [])
        .map(mapTaskFromServer)
        .filter(task => Number(task.projectId) === id);

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

async function addProjectMember(projectId, userId) {
    const project = getProject(projectId);
    if (!project || !isProjectAdmin(project)) {
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

async function removeProjectMember(projectId, userId) {
    const project = getProject(projectId);
    if (!project || !isProjectAdmin(project)) return false;
    if (Number(userId) === Number(project.adminId)) return false;

    const nickname = getNicknameById(userId);
    if (!confirm(`Удалить @${nickname} из проекта?`)) return false;

    await api("DELETE", `/projects/${Number(projectId)}/members/${Number(userId)}`);
    await loadProjectDetails(projectId);
    showToast("✓ Участник удалён");
    return true;
}

async function inviteProjectMember(projectId, userId) {
    const project = getProject(projectId);
    if (!project || !isProjectAdmin(project)) {
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