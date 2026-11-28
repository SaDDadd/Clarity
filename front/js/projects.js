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
    return Boolean(currentUser?.id != null && (isProjectAdmin(project) ||
        (isProjectMember(project) && project.role === "curator")));
}

function getProjectRole(project) {
    if (isProjectAdmin(project)) return "admin";
    if (!isProjectMember(project)) return null;
    return project.role === "curator" ? "curator" : "member";
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
        const knownName = cleanNickname(member?.username || member?.nickname || member?.name);
        if (knownName) userCache.set(numberId, knownName);
        const nickname = userCache.get(numberId) || knownName;
        const email = String(member?.email || "");

        let role = numberId === Number(currentUser?.id) ? getProjectRole(project) : member?.role;
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
let workspaceRequest = 0;
const projectRequests = new Map();
function invalidateProjectReads(projectId) {
    workspaceRequest++;
    projectRequests.delete(Number(projectId));
}
function validateProjectData(name, description) {
    if (!name.trim() || name.trim().length > 100) throw new Error("Название проекта: от 1 до 100 символов");
    if (description.trim().length > 1000) throw new Error("Описание проекта: не более 1000 символов");
}
async function refreshProjectAfterWrite(projectId, generation) {
    try { await loadProjectDetails(projectId); }
    catch (error) {
        if (generation === sessionGeneration) showToast("Изменения сохранены, но не удалось обновить данные: " + getErrorMessage(error));
    }
}
async function loadWorkspaceFromServer() {
    const request = ++workspaceRequest;
    const generation = sessionGeneration;
    const [projectResult, assignedResult] = await Promise.all([
        apiAll("/projects/all"),
        apiAll("/tasks/all")
    ]);

    assertSession(generation);
    if (request !== workspaceRequest) return false;
    const rawProjects = projectResult;
    const rawTasks = assignedResult;


    projects = rawProjects
        .map(mapProjectFromServer)
        .filter(project => Number.isInteger(project.id));

    tasks = rawTasks
        .map(mapTaskFromServer)
        .filter(task => Number.isInteger(task.id));

    projectRequests.clear();
    currentProjectDetails = null;
    projectTaskCache.clear();
    projects.forEach(project => projectTaskCache.set(project.id, []));
    tasks.forEach(task => {
        const id = Number(task.projectId);
        if (!projectTaskCache.has(id)) projectTaskCache.set(id, []);
        projectTaskCache.get(id).push(task);
    });

    validateCurrentProject();
    return true;
}

// Загрузка деталей конкретного проекта и его задач
async function loadProjectDetails(projectId) {
    const id = Number(projectId);
    const generation = sessionGeneration;
    const request = Symbol();
    projectRequests.set(id, request);
    const [detailsResult, taskResult] = await Promise.all([
        api("GET", `/projects/${id}`),
        apiAll(`/projects/${id}/tasks`)
    ]);

    if (generation !== sessionGeneration || projectRequests.get(id) !== request || !getProject(id)) return;
    const mappedProject = mapProjectFromServer(detailsResult);
    if (mappedProject.id !== id) throw new Error("Сервер вернул другой проект");
    const index = projects.findIndex(project => Number(project.id) === id);
    if (index >= 0) projects[index] = mappedProject;
    else projects.push(mappedProject);

    // Бэкенд FastAPI возвращает объект с массивом внутри поля items
    const rawTasks = taskResult;
    const mappedTasks = rawTasks.map(mapTaskFromServer).filter(task => Number(task.projectId) == id);

    projectTaskCache.set(id, mappedTasks);
    tasks = tasks.filter(task => Number(task.projectId) !== id);
    tasks.push(...mappedTasks);

    if (Number(currentProjectId) === id) currentProjectDetails = mappedProject;
    mappedTasks.forEach(task => {
        if (task.assigneeId) ensureUserCached(task.assigneeId);
    });

    if (Number(elements.projectForm.dataset.editingId) === id) renderProjectMembers(id);
    if (!elements.membersModal.classList.contains("hidden") && Number(currentProjectId) === id) renderMembersModal();
    if (currentPage !== "settings") render();
}

// Создание нового проекта
async function createProject(name, description) {
    if (!currentUser) return false;
    validateProjectData(name, description);
    return withWriteLock("project:create", async generation => {
        const result = await api("POST", "/projects", {
            project_name: name.trim(), project_description: description.trim()
        });
        assertSession(generation);
        const project = mapProjectFromServer(result);
        invalidateProjectReads(project.id);
        if (!Number.isInteger(project.id) || project.id <= 0) {
            showToast("Проект создан, обновите данные для отображения");
            return true;
        }
        projects = projects.filter(item => item.id !== project.id);
        projects.push(project);
        projectTaskCache.set(project.id, []);
        currentProjectId = project.id;
        currentPage = "overview";
        saveSettings(); render(); showToast("✓ Проект создан — вы администратор");
        return true;
    });
}

async function updateProject(projectId, name, description) {
    const project = getProject(projectId);
    if (!project || !canManageProject(project)) { showToast("Только администратор или куратор могут изменять проект"); return false; }
    validateProjectData(name, description);
    const patch = {};
    if (name.trim() !== project.name) patch.project_name = name.trim();
    if (description.trim() !== project.description) patch.project_description = description.trim();
    if (!Object.keys(patch).length) return true;
    return withWriteLock(`project:${project.id}`, async generation => {
        await api("PUT", `/projects/${project.id}`, patch);
        assertSession(generation); invalidateProjectReads(project.id);
        const live = getProjectRaw(project.id);
        if (live) { if (patch.project_name !== undefined) live.name = patch.project_name; if (patch.project_description !== undefined) live.description = patch.project_description; }
        render(); showToast("✓ Проект обновлён");
        return true;
    });
}

function removeLocalProject(projectId) {
    const id = Number(projectId);
    invalidateProjectReads(id);
    projects = projects.filter(item => item.id !== id);
    tasks = tasks.filter(task => task.projectId !== id);
    projectTaskCache.delete(id);
    if (Number(currentProjectId) === id) { currentProjectId = null; currentProjectDetails = null; }
    validateCurrentProject();
    if (Number(elements.projectForm.dataset.editingId) === id) closeProjectModal();
    closeMembersModal(); closeAllFloatingMenus();
    saveSettings(); render();
}

async function deleteProject(projectId) {
    const project = getProject(projectId);
    if (!project || !isProjectAdmin(project)) { showToast("Только администратор может удалить проект"); return false; }
    return withWriteLock(`project:${project.id}`, async generation => {
        if (!confirm(`Удалить проект "${project.name}"?`)) return false;
        await api("DELETE", `/projects/${project.id}`);
        assertSession(generation); removeLocalProject(project.id);
        showToast("✓ Проект удалён"); return true;
    });
}

async function leaveProject(projectId) {
    const project = getProject(projectId);
    if (!project) return false;
    const extra = isProjectAdmin(project) ? " Если других участников нет, сервер удалит проект; иначе назначит нового администратора." : " Ваши задачи будут сняты с вас.";
    return withWriteLock(`project:${project.id}`, async generation => {
        if (!confirm(`Выйти из проекта «${project.name}»?${extra}`)) return false;
        await api("DELETE", `/projects/${project.id}/leave`);
        assertSession(generation); removeLocalProject(project.id);
        showToast("✓ Вы вышли из проекта"); return true;
    });
}

// Выбор проекта для просмотра
async function selectProject(projectId) {
    const project = getProject(projectId);
    if (!project) return;
    currentProjectId = Number(projectId);
    currentProjectDetails = null;
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

// Управление участниками и приглашениями
async function addProjectMember(projectId, userId) {
    const project = getProject(projectId);
    const id = Number(userId);
    if (!canManageProject(project) || !Number.isInteger(id) || id <= 0 || id === Number(currentUser?.id) || id === project.adminId || project.memberIds.includes(id)) return false;
    return withWriteLock(`project:${project.id}`, async generation => {
        await api("POST", `/projects/${project.id}/members`, { user_id: id });
        assertSession(generation); invalidateProjectReads(project.id);
        await refreshProjectAfterWrite(project.id, generation);
        assertSession(generation); showToast("✓ Участник добавлен"); return true;
    });
}

async function removeProjectMember(projectId, userId) {
    const project = getProject(projectId);
    const id = Number(userId);
    if (!canManageProject(project) || id === project.adminId || id === Number(currentUser?.id) || !project.memberIds.includes(id)) return false;
    return withWriteLock(`project:${project.id}`, async generation => {
        if (!confirm(`Удалить @${getNicknameById(id)} из проекта?`)) return false;
        await api("DELETE", `/projects/${project.id}/members/${id}`);
        assertSession(generation); invalidateProjectReads(project.id);
        const live = getProjectRaw(project.id);
        if (live) { live.memberIds = live.memberIds.filter(value => value !== id); live.members = live.members.filter(member => Number(member.user_id ?? member.id) !== id); }
        tasks.forEach(task => { if (task.projectId === project.id && task.assigneeId === id) task.assigneeId = null; });
        render(); await refreshProjectAfterWrite(project.id, generation);
        assertSession(generation); showToast("✓ Участник удалён"); return true;
    });
}

async function inviteProjectMember(projectId, userId) {
    const project = getProject(projectId);
    const id = Number(userId);
    if (!canManageProject(project) || !Number.isInteger(id) || id <= 0 || id === Number(currentUser?.id) || id === project.adminId || project.memberIds.includes(id)) return false;
    return withWriteLock(`invite:${project.id}:${id}`, async generation => {
        await api("POST", `/projects/${project.id}/invitations`, { user_id: id, message: `Приглашение в проект «${project.name}»` });
        assertSession(generation);
        showToast("✓ Приглашение отправлено");
        if (Number(elements.projectForm.dataset.editingId) === project.id) await renderProjectInvitations(project.id);
        return true;
    });
}

async function changeMemberRole(projectId, userId, role) {
    const project = getProject(projectId);
    const id = Number(userId);
    if (!canManageProject(project) || !["member", "curator"].includes(role) || id === project.adminId || id === Number(currentUser?.id) || !project.memberIds.includes(id)) return false;
    return withWriteLock(`project:${project.id}`, async generation => {
        await api("PATCH", `/projects/${project.id}/members/${id}/role?role=${encodeURIComponent(role)}`);
        assertSession(generation); invalidateProjectReads(project.id);
        const member = getProjectRaw(project.id)?.members.find(item => Number(item.user_id ?? item.id) === id);
        if (member) member.role = role;
        await refreshProjectAfterWrite(project.id, generation);
        assertSession(generation); showToast("✓ Роль обновлена"); return true;
    });
}

async function transferProjectAdmin(projectId, userId) {
    const project = getProject(projectId);
    const id = Number(userId);
    if (!isProjectAdmin(project) || id === project.adminId || !project.memberIds.includes(id)) return false;
    return withWriteLock(`project:${project.id}`, async generation => {
        if (!confirm(`Передать администрирование @${getNicknameById(id)}? Вы станете куратором.`)) return false;
        await api("PATCH", `/projects/${project.id}/admin`, { new_admin_id: id });
        assertSession(generation); invalidateProjectReads(project.id);
        const live = getProjectRaw(project.id);
        if (live) {
            const old = live.adminId;
            live.adminId = live.ownerId = id; live.role = "curator";
            live.memberIds = [...new Set([...live.memberIds.filter(value => value !== id), old])];
            live.members.forEach(member => { const mid = Number(member.user_id ?? member.id); if (mid === id) member.role = "admin"; else if (mid === old) member.role = "curator"; });
        }
        if (Number(elements.projectForm.dataset.editingId) === project.id) { elements.deleteProjectButton.classList.add("hidden"); renderProjectMembers(project.id); }
        render(); await refreshProjectAfterWrite(project.id, generation);
        assertSession(generation); showToast("✓ Администрирование передано"); return true;
    });
}
