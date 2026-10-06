const STORAGE = {
    settings: "tasker_settings",
    currentProject: "tasker_current_project",
    currentPage: "tasker_current_page",
    currentView: "tasker_current_view"
};

const STATUS = {
    todo: "К выполнению",
    progress: "В работе",
    done: "Готово"
};

const statusFromBackend = {
    pending: "todo",
    in_progress: "progress",
    completed: "done"
};

const statusToBackend = {
    todo: "pending",
    progress: "in_progress",
    done: "completed"
};

const PRIORITY = {
    high: "Высокий",
    medium: "Средний",
    low: "Низкий"
};

const DEFAULT_SETTINGS = {
    theme: "light",
    sort: "newest"
};

const DEFAULT_USER = {
    id: null,
    name: "Пользователь",
    nickname: "Пользователь",
    email: "",
    createdAt: null
};

let currentUser = null;
let authMode = "login";
let projects = [];
let tasks = [];
let settings = { ...DEFAULT_SETTINGS };
let user = { ...DEFAULT_USER };
let currentProjectId = null;
let currentPage = "overview";
let currentView = "board";
let currentTaskMenuId = null;
let draggedTaskId = null;
let calendarCursor = new Date();
let currentProjectDetails = null;
let invitations = [];
let projectTaskCache = new Map();
const userCache = new Map();

const filters = {
    status: "all",
    priority: "all",
    project: "all",
    overdue: false
};

const elements = {
    app: document.getElementById("app"),
    authScreen: document.getElementById("authScreen"),
    authForm: document.getElementById("authForm"),
    loginTab: document.getElementById("loginTab"),
    registerTab: document.getElementById("registerTab"),
    authNameField: document.getElementById("authNameField"),
    authNameInput: document.getElementById("authNameInput"),
    authLoginLabel: document.getElementById("authLoginLabel"),
    authEmailInput: document.getElementById("authEmailInput"),
    authPasswordInput: document.getElementById("authPasswordInput"),
    authConfirmField: document.getElementById("authConfirmField"),
    authConfirmInput: document.getElementById("authConfirmInput"),
    authMessage: document.getElementById("authMessage"),
    authSubmitButton: document.getElementById("authSubmitButton"),
    logoutButton: document.getElementById("logoutButton"),
    projectsList: document.getElementById("projectsList"),
    projectsPageButton: document.getElementById("projectsPageButton"),
    board: document.getElementById("board"),
    projectTitle: document.getElementById("projectTitle"),
    projectDescription: document.getElementById("projectDescription"),
    breadcrumb: document.getElementById("breadcrumb"),
    breadcrumbProject: document.getElementById("breadcrumbProject"),
    createTaskButton: document.getElementById("createTaskButton"),
    createTaskButtonText: document.getElementById("createTaskButtonText"),
    toolbar: document.getElementById("toolbar"),
    views: document.getElementById("views"),
    addProjectButton: document.getElementById("addProjectButton"),
    searchInput: document.getElementById("searchInput"),
    taskModal: document.getElementById("taskModal"),
    projectModal: document.getElementById("projectModal"),
    closeTaskModal: document.getElementById("closeTaskModal"),
    closeProjectModal: document.getElementById("closeProjectModal"),
    cancelTaskButton: document.getElementById("cancelTaskButton"),
    cancelProjectButton: document.getElementById("cancelProjectButton"),
    taskForm: document.getElementById("taskForm"),
    projectForm: document.getElementById("projectForm"),
    taskMenu: document.getElementById("taskMenu"),
    filterMenu: document.getElementById("filterMenu"),
    sortMenu: document.getElementById("sortMenu"),
    filterButton: document.getElementById("filterButton"),
    sortButton: document.getElementById("sortButton"),
    filterStatus: document.getElementById("filterStatus"),
    filterPriority: document.getElementById("filterPriority"),
    filterProject: document.getElementById("filterProject"),
    filterProjectLabel: document.getElementById("filterProjectLabel"),
    filterOverdue: document.getElementById("filterOverdue"),
    resetFiltersButton: document.getElementById("resetFiltersButton"),
    sortSelect: document.getElementById("sortSelect"),
    taskTitleInput: document.getElementById("taskTitleInput"),
    taskDescriptionInput: document.getElementById("taskDescriptionInput"),
    taskProjectInput: document.getElementById("taskProjectInput"),
    taskStatusInput: document.getElementById("taskStatusInput"),
    taskPriorityInput: document.getElementById("taskPriorityInput"),
    taskDateInput: document.getElementById("taskDateInput"),
    taskAssigneeField: document.getElementById("taskAssigneeField"),
    taskAssigneeInput: document.getElementById("taskAssigneeInput"),
    taskFavoriteInput: document.getElementById("taskFavoriteInput"),
    taskModalTitle: document.getElementById("taskModalTitle"),
    taskModalSubtitle: document.getElementById("taskModalSubtitle"),
    taskSubmitButton: document.getElementById("taskSubmitButton"),
    deleteTaskButton: document.getElementById("deleteTaskButton"),
    projectNameInput: document.getElementById("projectNameInput"),
    projectDescriptionInput: document.getElementById("projectDescriptionInput"),
    projectModalTitle: document.getElementById("projectModalTitle"),
    projectModalSubtitle: document.getElementById("projectModalSubtitle"),
    projectSubmitButton: document.getElementById("projectSubmitButton"),
    deleteProjectButton: document.getElementById("deleteProjectButton"),
    projectMembersSection: document.getElementById("projectMembersSection"),
    projectRoleBadge: document.getElementById("projectRoleBadge"),
    projectMembersList: document.getElementById("projectMembersList"),
    projectMemberSearchWrap: document.getElementById("projectMemberSearchWrap"),
    projectMemberSearch: document.getElementById("projectMemberSearch"),
    projectMemberSearchResults: document.getElementById("projectMemberSearchResults"),
    toastContainer: document.getElementById("toastContainer"),
    sidebarUserName: document.getElementById("sidebarUserName"),
    sidebarUserEmail: document.getElementById("sidebarUserEmail"),
    sidebarAvatar: document.getElementById("sidebarAvatar"),
    topAvatar: document.getElementById("topAvatar"),
    helpButton: document.getElementById("helpButton"),
    notificationButton: document.getElementById("notificationButton")
};

function userStorageKey(baseKey) {
    return currentUser?.id ? `${baseKey}::${currentUser.id}` : baseKey;
}

function loadSettings() {
    try {
        const raw = localStorage.getItem(userStorageKey(STORAGE.settings));
        return raw ? { ...DEFAULT_SETTINGS, ...JSON.parse(raw) } : { ...DEFAULT_SETTINGS };
    } catch {
        return { ...DEFAULT_SETTINGS };
    }
}

function saveSettings() {
    if (!currentUser) return;
    localStorage.setItem(userStorageKey(STORAGE.settings), JSON.stringify(settings));
    localStorage.setItem(userStorageKey(STORAGE.currentPage), currentPage);
    localStorage.setItem(userStorageKey(STORAGE.currentView), currentView);
    if (currentProjectId !== null && currentProjectId !== undefined) {
        localStorage.setItem(userStorageKey(STORAGE.currentProject), String(currentProjectId));
    } else {
        localStorage.removeItem(userStorageKey(STORAGE.currentProject));
    }
}

function clearLocalWorkspace() {
    projects = [];
    tasks = [];
    invitations = [];
    projectTaskCache.clear();
    currentProjectDetails = null;
    currentProjectId = null;
    currentPage = "overview";
    currentView = "board";
    userCache.clear();
}

function cleanNickname(value) {
    return String(value || "").trim().replace(/^@+/, "");
}

function normalizeNickname(value) {
    return cleanNickname(value).toLowerCase();
}

function validateNickname(nickname) {
    if (nickname.length < 3 || nickname.length > 30) {
        throw new Error("Ник должен содержать от 3 до 30 символов.");
    }
    if (!/^[A-Za-zА-Яа-яЁё0-9._-]+$/.test(nickname)) {
        throw new Error("В нике разрешены буквы, цифры, точка, дефис и подчёркивание.");
    }
}

function mapProfileFromServer(profile) {
    const nickname = cleanNickname(profile?.username || "Пользователь");
    const mapped = {
        id: Number(profile?.user_id),
        username: nickname,
        nickname,
        name: nickname,
        email: String(profile?.email || ""),
        createdAt: profile?.created_date || null
    };
    currentUser = mapped;
    user = { ...DEFAULT_USER, ...mapped };
    userCache.set(mapped.id, nickname);
    return mapped;
}

function mapTaskFromServer(task) {
    const rawStatus = String(task?.task_status || task?.status || "pending");
    return {
        id: Number(task?.task_id ?? task?.id),
        projectId: Number(task?.project_id ?? task?.projectId),
        assigneeId: task?.assigned_to == null ? null : Number(task.assigned_to),
        title: String(task?.title || "Без названия"),
        description: String(task?.task_description ?? task?.description ?? ""),
        priority: ["high", "medium", "low"].includes(task?.task_priority) ? task.task_priority : "medium",
        date: task?.deadline ? String(task.deadline).slice(0, 10) : "",
        status: statusFromBackend[rawStatus] || "todo",
        favorite: Boolean(task?.task_favorite),
        createdAt: task?.created_date || null,
        updatedAt: task?.updated_date || task?.created_date || null
    };
}

function mapTaskToServer(payload) {
    const result = {
        title: String(payload.title || "").trim(),
        task_description: String(payload.description || "").trim(),
        task_status: statusToBackend[payload.status] || payload.status || "pending",
        task_priority: ["low", "medium", "high"].includes(payload.priority) ? payload.priority : "medium",
        task_favorite: Boolean(payload.favorite),
        assigned_to: payload.assigneeId === "" || payload.assigneeId == null ? null : Number(payload.assigneeId),
        deadline: payload.date ? String(payload.date).slice(0, 10) : null
    };
    return result;
}

function mapProjectFromServer(project) {
    const adminId = Number(project?.admin_id ?? project?.adminId);
    const members = Array.isArray(project?.members) ? project.members : [];
    const memberIds = members
        .map(member => Number(member?.user_id ?? member?.id))
        .filter(id => Number.isInteger(id) && id !== adminId);

    return {
        id: Number(project?.project_id ?? project?.id),
        adminId,
        ownerId: adminId,
        name: String(project?.project_name ?? project?.name ?? "Без названия"),
        description: String(project?.project_description ?? project?.description ?? ""),
        memberIds: [...new Set(memberIds)],
        role: project?.role || (adminId === currentUser?.id ? "admin" : "member"),
        createdAt: project?.created_date || null,
        members
    };
}

function getInvitationId(invitation) {
    return Number(invitation?.invitation_id ?? invitation?.id);
}

function mapInvitation(invitation) {
    return {
        id: getInvitationId(invitation),
        projectId: Number(invitation?.project_id ?? invitation?.project?.project_id),
        projectName: String(invitation?.project_name ?? invitation?.project?.project_name ?? "Проект"),
        inviterId: invitation?.inviter_id == null ? null : Number(invitation.inviter_id),
        message: String(invitation?.message || ""),
        createdAt: invitation?.created_date || invitation?.createdAt || null,
        raw: invitation
    };
}

function escapeHTML(value) {
    const div = document.createElement("div");
    div.textContent = value ?? "";
    return div.innerHTML;
}

function escapeAttribute(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function formatDate(date) {
    if (!date) return "Без срока";
    const parts = String(date).slice(0, 10).split("-");
    return parts.length === 3 ? `${parts[2]}.${parts[1]}.${parts[0]}` : date;
}

function getTodayISO() {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
}

function isOverdue(task) {
    return Boolean(task.date && task.date < getTodayISO() && task.status !== "done");
}

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

function getInitials(name) {
    const text = String(name || "C").trim();
    if (!text) return "C";
    return text.split(/\s+/).slice(0, 2).map(part => part[0]?.toUpperCase() || "").join("") || "C";
}

function showToast(message) {
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = message;
    elements.toastContainer.appendChild(toast);
    setTimeout(() => toast.remove(), 2600);
}

function getErrorMessage(error) {
    return error?.message || "Не удалось выполнить операцию.";
}

function closeAllFloatingMenus() {
    closeTaskMenu();
    elements.filterMenu.classList.add("hidden");
    elements.sortMenu.classList.add("hidden");
}

function positionFloatingMenu(menu, button, width = 230) {
    const rect = button.getBoundingClientRect();
    menu.classList.remove("hidden");
    let left = rect.right - width;
    let top = rect.bottom + 7;
    if (left < 10) left = 10;
    if (left + width > window.innerWidth - 10) left = window.innerWidth - width - 10;
    if (top + menu.offsetHeight > window.innerHeight - 10) top = rect.top - menu.offsetHeight - 7;
    menu.style.left = `${left}px`;
    menu.style.top = `${Math.max(10, top)}px`;
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

async function loadInvitations() {
    const result = await api("GET", "/invitations");
    invitations = (Array.isArray(result) ? result : []).map(mapInvitation);
    renderInvitationsSidebar();
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

function renderProjectsSidebar() {
    elements.projectsList.innerHTML = "";

    getAccessibleProjects().forEach(project => {
        const admin = isProjectAdmin(project);
        const item = document.createElement("a");
        item.href = `#project-${project.id}`;
        item.className = "project";
        if (currentPage === "overview" && Number(project.id) === Number(currentProjectId)) {
            item.classList.add("active-project");
        }

        item.innerHTML = `
            <span class="project-dot purple"></span>
            <span class="project-name">${escapeHTML(project.name)}</span>
            <span class="project-role-badge ${admin ? "" : "member"}">${admin ? "A" : "У"}</span>
            ${admin ? `
                <span class="project-actions">
                    <button class="project-edit" type="button" aria-label="Редактировать проект">✎</button>
                    <button class="project-delete" type="button" aria-label="Удалить проект">×</button>
                </span>
            ` : ""}
        `;

        item.addEventListener("click", event => {
            event.preventDefault();
            if (event.target.closest(".project-edit") || event.target.closest(".project-delete")) return;
            selectProject(project.id);
        });

        item.querySelector(".project-edit")?.addEventListener("click", event => {
            event.preventDefault();
            event.stopPropagation();
            openProjectModal(project.id);
        });

        item.querySelector(".project-delete")?.addEventListener("click", async event => {
            event.preventDefault();
            event.stopPropagation();
            try {
                await deleteProject(project.id);
            } catch (error) {
                showToast(getErrorMessage(error));
            }
        });

        elements.projectsList.appendChild(item);
    });

    renderInvitationsSidebar();
}

function ensureInvitationNav() {
    let nav = document.getElementById("invitationsNavItem");
    if (nav) return nav;

    nav = document.createElement("a");
    nav.id = "invitationsNavItem";
    nav.href = "#invitations";
    nav.className = "nav-item";
    nav.dataset.page = "invitations";
    nav.innerHTML = `<span>✉</span><span>Входящие приглашения</span><span class="invitation-count" style="margin-left:auto"></span>`;
    nav.addEventListener("click", event => {
        event.preventDefault();
        setPage("invitations");
    });

    const navRoot = document.querySelector(".navigation");
    navRoot?.appendChild(nav);
    return nav;
}

function renderInvitationsSidebar() {
    const nav = ensureInvitationNav();
    nav.classList.toggle("active", currentPage === "invitations");
    const count = nav.querySelector(".invitation-count");
    if (count) count.textContent = invitations.length ? String(invitations.length) : "";
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

async function renderProjectMemberSearchResults(projectId, query) {
    const project = getProject(projectId);
    if (!project || !isProjectAdmin(project)) return;

    const normalizedQuery = normalizeNickname(query);
    elements.projectMemberSearchResults.innerHTML = "";
    if (normalizedQuery.length < 2) return;

    try {
        const accounts = await searchUsers(normalizedQuery);
        const filtered = accounts
            .filter(account => Number(account.id) !== Number(project.adminId))
            .slice(0, 8);

        filtered.forEach(account => userCache.set(Number(account.id), account.username));

        if (!filtered.length) {
            elements.projectMemberSearchResults.innerHTML = `<div class="member-search-empty">Пользователи не найдены.</div>`;
            return;
        }

        filtered.forEach(account => {
            const isMember = project.memberIds.some(id => Number(id) === Number(account.id));
            const row = document.createElement("div");
            row.className = "project-member-result";
            row.innerHTML = `
                <div class="project-member-identity">
                    <div class="member-avatar">${escapeHTML(getInitials(account.username))}</div>
                    <div class="project-member-copy">
                        <strong>@${escapeHTML(account.username)}</strong>
                        <span>${escapeHTML(account.email)}</span>
                    </div>
                </div>
                ${isMember
                    ? `<span class="role-badge member">Уже участник</span>`
                    : `<button class="member-add-button" type="button">Пригласить</button>`}
            `;

            row.querySelector(".member-add-button")?.addEventListener("click", async () => {
                try {
                    await inviteProjectMember(project.id, account.id);
                } catch (error) {
                    showToast(getErrorMessage(error));
                }
            });
            elements.projectMemberSearchResults.appendChild(row);
        });
    } catch (error) {
        elements.projectMemberSearchResults.innerHTML = `<div class="member-search-empty">${escapeHTML(getErrorMessage(error))}</div>`;
    }
}

async function renderProjectInvitations(projectId) {
    const project = getProject(projectId);
    if (!project || !isProjectAdmin(project)) return;

    let section = document.getElementById("projectInvitationsSection");
    if (!section) {
        section = document.createElement("div");
        section.id = "projectInvitationsSection";
        section.className = "project-members-list";
        section.style.marginTop = "12px";
        elements.projectMembersSection.appendChild(section);
    }

    section.innerHTML = `<div class="project-members-heading"><strong>Отправленные приглашения</strong></div>`;

    try {
        const result = await api("GET", `/invitations/project/${Number(projectId)}`);
        const list = Array.isArray(result) ? result : [];

        if (!list.length) {
            section.insertAdjacentHTML("beforeend", `<div class="member-search-empty">Нет активных приглашений.</div>`);
            return;
        }

        list.forEach(raw => {
            const invitation = mapInvitation(raw);
            const recipientId = raw?.user_id ?? raw?.recipient_id ?? raw?.invitee_id;
            const recipientName = raw?.username || raw?.recipient_username || (recipientId ? getNicknameById(recipientId) : "Пользователь");
            if (recipientId) userCache.set(Number(recipientId), cleanNickname(recipientName));

            const row = document.createElement("div");
            row.className = "project-member-row";
            row.innerHTML = `
                <div class="project-member-identity">
                    <div class="member-avatar">${escapeHTML(getInitials(recipientName))}</div>
                    <div class="project-member-copy">
                        <strong>@${escapeHTML(cleanNickname(recipientName))}</strong>
                        <span>${escapeHTML(invitation.message || "Приглашение отправлено")}</span>
                    </div>
                </div>
                <div class="member-actions">
                    <span class="role-badge member">Ожидает</span>
                    <button class="member-remove-button" type="button">Отменить</button>
                </div>
            `;

            row.querySelector(".member-remove-button").addEventListener("click", async () => {
                try {
                    await deleteInvitation(invitation.id);
                    await renderProjectInvitations(projectId);
                } catch (error) {
                    showToast(getErrorMessage(error));
                }
            });

            section.appendChild(row);
        });
    } catch (error) {
        section.insertAdjacentHTML("beforeend", `<div class="member-search-empty">${escapeHTML(getErrorMessage(error))}</div>`);
    }
}

function renderProjectMembers(projectId) {
    const project = getProject(projectId);
    if (!project) return;

    const admin = isProjectAdmin(project);
    elements.projectMembersSection.classList.remove("hidden");
    elements.projectRoleBadge.textContent = admin ? "Администратор" : "Участник";
    elements.projectRoleBadge.classList.toggle("member", !admin);
    elements.projectMemberSearchWrap.classList.toggle("hidden", !admin);

    const accounts = getProjectAccounts(projectId);
    elements.projectMembersList.innerHTML = "";

    accounts.forEach(account => {
        const isAdminAccount = Number(account.id) === Number(project.adminId);
        const row = document.createElement("div");
        row.className = "project-member-row";
        row.innerHTML = `
            <div class="project-member-identity">
                <div class="member-avatar">${escapeHTML(getInitials(account.nickname || account.name))}</div>
                <div class="project-member-copy">
                    <strong>@${escapeHTML(account.nickname || account.name)}</strong>
                    <span>${escapeHTML(account.email)}</span>
                </div>
            </div>
            <div class="member-actions">
                <span class="role-badge ${isAdminAccount ? "" : "member"}">${isAdminAccount ? "Админ" : "Участник"}</span>
                ${admin && !isAdminAccount ? `<button class="member-remove-button" type="button">Удалить</button>` : ""}
            </div>
        `;

        row.querySelector(".member-remove-button")?.addEventListener("click", async () => {
            try {
                await removeProjectMember(project.id, account.id);
            } catch (error) {
                showToast(getErrorMessage(error));
            }
        });
        elements.projectMembersList.appendChild(row);
    });

    if (admin) {
        renderProjectMemberSearchResults(project.id, elements.projectMemberSearch.value);
        renderProjectInvitations(project.id);
    }
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

    const result = await api(
        "PUT",
        `/projects/${Number(task.projectId)}/tasks/${Number(task.id)}`,
        mapTaskToServer(payload)
    );

    const mapped = mapTaskFromServer(result);
    const index = tasks.findIndex(item => Number(item.id) === Number(task.id));
    if (index >= 0) tasks[index] = mapped;

    closeTaskMenu();
    render();
    showToast(mapped.favorite ? "✓ Добавлено в избранное" : "Удалено из избранного");
    return true;
}

function getBaseTasksForPage() {
    const accessible = tasks.filter(task => Boolean(getProject(task.projectId)));
    if (currentPage === "overview") return getProjectTasks();
    if (currentPage === "favorites") return accessible.filter(task => task.favorite);
    if (currentPage === "my-tasks") return accessible.filter(task => Number(task.assigneeId) === Number(currentUser?.id));
    return [];
}

function getVisibleTasks() {
    let result = getBaseTasksForPage();
    const query = elements.searchInput.value.trim().toLowerCase();

    if (query) {
        result = result.filter(task => {
            const projectName = getProjectName(task.projectId).toLowerCase();
            return task.title.toLowerCase().includes(query)
                || task.description.toLowerCase().includes(query)
                || projectName.includes(query);
        });
    }

    if (filters.status !== "all") result = result.filter(task => task.status === filters.status);
    if (filters.priority !== "all") result = result.filter(task => task.priority === filters.priority);
    if (filters.project !== "all" && currentPage !== "overview") {
        result = result.filter(task => Number(task.projectId) === Number(filters.project));
    }
    if (filters.overdue) result = result.filter(isOverdue);

    return sortTasks(result, settings.sort);
}

function sortTasks(list, sortType) {
    const priorityWeight = { high: 0, medium: 1, low: 2 };
    const statusWeight = { todo: 0, progress: 1, done: 2 };
    const copy = [...list];

    copy.sort((a, b) => {
        switch (sortType) {
            case "oldest":
                return new Date(a.createdAt || 0) - new Date(b.createdAt || 0);
            case "date-asc":
                return compareDates(a.date, b.date, 1);
            case "date-desc":
                return compareDates(a.date, b.date, -1);
            case "priority":
                return priorityWeight[a.priority] - priorityWeight[b.priority]
                    || new Date(b.createdAt || 0) - new Date(a.createdAt || 0);
            case "title":
                return a.title.localeCompare(b.title, "ru");
            case "status":
                return statusWeight[a.status] - statusWeight[b.status]
                    || new Date(b.createdAt || 0) - new Date(a.createdAt || 0);
            default:
                return new Date(b.createdAt || 0) - new Date(a.createdAt || 0);
        }
    });
    return copy;
}

function compareDates(a, b, direction) {
    if (!a && !b) return 0;
    if (!a) return 1;
    if (!b) return -1;
    return String(a).localeCompare(String(b)) * direction;
}

function resetFilters(shouldRender = true) {
    filters.status = "all";
    filters.priority = "all";
    filters.project = "all";
    filters.overdue = false;
    syncFilterControls();
    if (shouldRender) renderContent();
}

function syncFilterControls() {
    elements.filterStatus.value = filters.status;
    elements.filterPriority.value = filters.priority;
    elements.filterProject.value = filters.project;
    elements.filterOverdue.checked = filters.overdue;
    elements.sortSelect.value = settings.sort;

    const activeCount = [
        filters.status !== "all",
        filters.priority !== "all",
        filters.project !== "all" && currentPage !== "overview",
        filters.overdue
    ].filter(Boolean).length;

    elements.filterButton.textContent = activeCount ? `Фильтр (${activeCount})` : "Фильтр";
}

function populateFilterProjects() {
    const accessibleProjects = getAccessibleProjects();
    elements.filterProject.innerHTML =
        `<option value="all">Все проекты</option>` +
        accessibleProjects.map(project => `<option value="${project.id}">${escapeHTML(project.name)}</option>`).join("");

    if (filters.project !== "all" && !getProject(filters.project)) filters.project = "all";
    elements.filterProject.value = filters.project;
    elements.filterProjectLabel.classList.toggle("hidden", currentPage === "overview");
}

function createTaskElement(task, draggable = false) {
    const element = document.createElement("article");
    const assigneeName = task.assigneeId ? getNicknameById(task.assigneeId) : "Не назначен";
    const canDrag = draggable && canChangeTaskStatus(task);

    element.className = "task-card";
    element.dataset.taskId = task.id;
    element.draggable = canDrag;
    if (task.status === "done") element.classList.add("completed");
    if (isOverdue(task)) element.classList.add("overdue");

    element.innerHTML = `
        <div class="task-top">
            <span class="priority ${task.priority}">${PRIORITY[task.priority]}</span>
            <div class="task-top-actions">
                <button class="favorite-button ${task.favorite ? "active" : ""}" type="button" aria-label="Избранное">${task.favorite ? "★" : "☆"}</button>
                <button class="more" type="button" aria-label="Действия">⋯</button>
            </div>
        </div>
        <h3>${escapeHTML(task.title)}</h3>
        ${task.description ? `<p>${escapeHTML(task.description)}</p>` : ""}
        <div class="task-footer">
            <span class="date">${task.status === "done" ? "✓ Выполнено" : `${isOverdue(task) ? "!" : "◷"} ${formatDate(task.date)}`}</span>
            <div class="task-assignee-chip" title="Исполнитель: @${escapeAttribute(assigneeName)}">
                <div class="task-avatar">${escapeHTML(getInitials(assigneeName))}</div>
                <span>${task.assigneeId ? `@${escapeHTML(assigneeName)}` : "Не назначен"}</span>
            </div>
        </div>
    `;

    element.addEventListener("click", () => openTaskModal("todo", task.id));
    element.querySelector(".favorite-button").addEventListener("click", async event => {
        event.stopPropagation();
        try { await toggleFavorite(task.id); } catch (error) { showToast(getErrorMessage(error)); }
    });
    element.querySelector(".more").addEventListener("click", event => {
        event.stopPropagation();
        openTaskMenu(task.id, event.currentTarget);
    });

    if (task.assigneeId) ensureUserCached(task.assigneeId).then(() => {
        if (document.body.contains(element)) {
            const chip = element.querySelector(".task-assignee-chip span");
            const avatar = element.querySelector(".task-avatar");
            const name = getNicknameById(task.assigneeId);
            if (chip) chip.textContent = `@${name}`;
            if (avatar) avatar.textContent = getInitials(name);
        }
    });

    if (canDrag) {
        element.addEventListener("dragstart", event => {
            draggedTaskId = Number(task.id);
            event.dataTransfer.effectAllowed = "move";
            event.dataTransfer.setData("text/plain", String(task.id));
            requestAnimationFrame(() => element.classList.add("dragging"));
        });
        element.addEventListener("dragend", () => {
            draggedTaskId = null;
            element.classList.remove("dragging");
            document.querySelectorAll(".tasks.drag-over").forEach(container => container.classList.remove("drag-over"));
        });
    }

    return element;
}

function createPageTaskCard(task) {
    const card = document.createElement("article");
    const assigneeName = task.assigneeId ? getNicknameById(task.assigneeId) : "Не назначен";
    card.className = "page-task-card";
    if (task.status === "done") card.style.opacity = "0.65";

    card.innerHTML = `
        <div class="page-task-main">
            <div class="page-task-title">
                <span class="priority ${task.priority}">${PRIORITY[task.priority]}</span>
                <strong>${escapeHTML(task.title)}</strong>
            </div>
            <div class="page-task-meta">
                <span>${escapeHTML(getProjectName(task.projectId))}</span>
                <span>${STATUS[task.status]}</span>
                <span>${task.date ? formatDate(task.date) : "Без срока"}</span>
                <span>Исполнитель: ${task.assigneeId ? `@${escapeHTML(assigneeName)}` : "не назначен"}</span>
                ${isOverdue(task) ? `<span style="color:var(--danger)">Просрочено</span>` : ""}
            </div>
        </div>
        <div class="page-task-actions">
            <button class="favorite-button ${task.favorite ? "active" : ""}" type="button">${task.favorite ? "★" : "☆"}</button>
            <button class="small-action edit-task" type="button">${canManageTask(task) ? "Редактировать" : "Открыть"}</button>
        </div>
    `;

    card.addEventListener("click", () => openTaskModal("todo", task.id));
    card.querySelector(".favorite-button").addEventListener("click", async event => {
        event.stopPropagation();
        try { await toggleFavorite(task.id); } catch (error) { showToast(getErrorMessage(error)); }
    });
    card.querySelector(".edit-task").addEventListener("click", event => {
        event.stopPropagation();
        openTaskModal("todo", task.id);
    });
    return card;
}

function renderBoardView() {
    elements.board.className = "board";
    elements.board.innerHTML = "";

    const project = getCurrentProject();
    if (!project) {
        renderEmptyState("Нет доступных проектов", "Создайте свой проект или попросите администратора добавить вас в существующий.", "Создать проект", () => openProjectModal());
        return;
    }

    const visibleTasks = getVisibleTasks();
    const columns = [
        { id: "todo", title: "К выполнению", color: "gray" },
        { id: "progress", title: "В работе", color: "orange" },
        { id: "done", title: "Готово", color: "green" }
    ];

    columns.forEach(column => {
        const columnElement = document.createElement("div");
        columnElement.className = "column";
        const columnTasks = visibleTasks.filter(task => task.status === column.id);

        columnElement.innerHTML = `
            <div class="column-header">
                <div class="column-title">
                    <span class="status-dot ${column.color}"></span>
                    <strong>${column.title}</strong>
                    <span class="task-count">${columnTasks.length}</span>
                </div>
                ${isProjectAdmin(project) ? `<button type="button" class="add-task-column" data-status="${column.id}" aria-label="Добавить задачу">+</button>` : ""}
            </div>
            <div class="tasks" data-status="${column.id}"></div>
        `;

        const container = columnElement.querySelector(".tasks");
        columnTasks.forEach(task => container.appendChild(createTaskElement(task, true)));
        attachDropZone(container, column.id);
        elements.board.appendChild(columnElement);
    });

    document.querySelectorAll(".add-task-column").forEach(button => {
        button.addEventListener("click", () => openTaskModal(button.dataset.status));
    });
}

function attachDropZone(container, status) {
    container.addEventListener("dragover", event => {
        const task = tasks.find(item => Number(item.id) === Number(draggedTaskId));
        if (!task || !canChangeTaskStatus(task)) return;
        event.preventDefault();
        event.dataTransfer.dropEffect = "move";
        container.classList.add("drag-over");
    });

    container.addEventListener("dragleave", event => {
        if (!container.contains(event.relatedTarget)) container.classList.remove("drag-over");
    });

    container.addEventListener("drop", async event => {
        event.preventDefault();
        container.classList.remove("drag-over");
        const taskId = draggedTaskId || Number(event.dataTransfer.getData("text/plain"));
        const task = tasks.find(item => Number(item.id) === Number(taskId));
        if (!task || task.status === status || !canChangeTaskStatus(task)) return;

        try { await changeTaskStatus(task.id, status); }
        catch (error) { showToast(getErrorMessage(error)); }
    });
}

function renderTableView(taskList = getVisibleTasks()) {
    elements.board.className = "board single-view";
    elements.board.innerHTML = "";

    if (!taskList.length) {
        renderEmptyState("Задач не найдено", "Измените фильтр, поисковый запрос или создайте новую задачу.");
        return;
    }

    const wrap = document.createElement("div");
    wrap.className = "list-view";
    wrap.innerHTML = `
        <table class="task-table">
            <thead>
                <tr>
                    <th>Название</th><th>Проект</th><th>Исполнитель</th>
                    <th>Приоритет</th><th>Срок</th><th>Статус</th><th class="star-cell">★</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    `;

    const tbody = wrap.querySelector("tbody");
    taskList.forEach(task => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td class="task-title-cell">${escapeHTML(task.title)}</td>
            <td>${escapeHTML(getProjectName(task.projectId))}</td>
            <td>${task.assigneeId ? `@${escapeHTML(getNicknameById(task.assigneeId))}` : "Не назначен"}</td>
            <td><span class="priority ${task.priority}">${PRIORITY[task.priority]}</span></td>
            <td style="${isOverdue(task) ? "color:var(--danger);font-weight:600;" : ""}">${task.date ? formatDate(task.date) : "Без срока"}</td>
            <td>${STATUS[task.status]}</td>
            <td class="star-cell"><button class="favorite-button ${task.favorite ? "active" : ""}" type="button">${task.favorite ? "★" : "☆"}</button></td>
        `;
        row.addEventListener("click", () => openTaskModal("todo", task.id));
        row.querySelector(".favorite-button").addEventListener("click", async event => {
            event.stopPropagation();
            try { await toggleFavorite(task.id); } catch (error) { showToast(getErrorMessage(error)); }
        });
        tbody.appendChild(row);
    });
    elements.board.appendChild(wrap);
}

function renderCalendarView() {
    elements.board.className = "board single-view";
    elements.board.innerHTML = "";

    const year = calendarCursor.getFullYear();
    const month = calendarCursor.getMonth();
    const monthNames = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"];
    const weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];

    const wrap = document.createElement("div");
    wrap.className = "calendar-wrap";
    wrap.innerHTML = `
        <div class="calendar-toolbar">
            <strong>${monthNames[month]} ${year}</strong>
            <div class="calendar-nav">
                <button type="button" data-calendar="prev" aria-label="Предыдущий месяц">‹</button>
                <button type="button" data-calendar="today">Сегодня</button>
                <button type="button" data-calendar="next" aria-label="Следующий месяц">›</button>
            </div>
        </div>
        <div class="calendar-grid"></div>
    `;

    const grid = wrap.querySelector(".calendar-grid");
    weekdays.forEach(day => {
        const header = document.createElement("div");
        header.className = "calendar-weekday";
        header.textContent = day;
        grid.appendChild(header);
    });

    const first = new Date(year, month, 1);
    const firstWeekday = (first.getDay() + 6) % 7;
    const gridStart = new Date(year, month, 1 - firstWeekday);
    const visibleTasks = getVisibleTasks().filter(task => task.date);

    for (let i = 0; i < 42; i++) {
        const date = new Date(gridStart);
        date.setDate(gridStart.getDate() + i);
        const iso = toLocalISO(date);
        const day = document.createElement("div");
        day.className = "calendar-day" + (date.getMonth() !== month ? " muted" : "");
        day.innerHTML = `<span class="calendar-day-number">${date.getDate()}</span>`;

        visibleTasks.filter(task => task.date === iso).forEach(task => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "calendar-task";
            button.textContent = task.title;
            button.title = `${task.title} — ${getProjectName(task.projectId)}`;
            button.addEventListener("click", () => openTaskModal("todo", task.id));
            day.appendChild(button);
        });
        grid.appendChild(day);
    }

    wrap.querySelector('[data-calendar="prev"]').addEventListener("click", () => {
        calendarCursor = new Date(year, month - 1, 1);
        renderCalendarView();
    });
    wrap.querySelector('[data-calendar="next"]').addEventListener("click", () => {
        calendarCursor = new Date(year, month + 1, 1);
        renderCalendarView();
    });
    wrap.querySelector('[data-calendar="today"]').addEventListener("click", () => {
        calendarCursor = new Date();
        renderCalendarView();
    });

    elements.board.appendChild(wrap);
}

function toLocalISO(date) {
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function renderTaskCollectionPage() {
    elements.board.className = "board single-view";
    elements.board.innerHTML = "";
    const visibleTasks = getVisibleTasks();

    if (!visibleTasks.length) {
        const title = currentPage === "favorites" ? "Нет избранных задач" : "Задач не найдено";
        const text = currentPage === "favorites"
            ? "Нажмите ☆ на карточке задачи, чтобы она появилась здесь."
            : "Создайте задачу в любом проекте или измените фильтры.";
        renderEmptyState(title, text);
        return;
    }

    const list = document.createElement("div");
    list.className = "page-list";
    visibleTasks.forEach(task => list.appendChild(createPageTaskCard(task)));
    elements.board.appendChild(list);
}

function renderProjectsPage() {
    elements.board.className = "board single-view";
    elements.board.innerHTML = "";

    const accessibleProjects = getAccessibleProjects();
    if (!accessibleProjects.length) {
        renderEmptyState("Нет проектов", "Создайте проект или дождитесь добавления в проект другим администратором.", "Создать проект", () => openProjectModal());
        return;
    }

    const grid = document.createElement("div");
    grid.className = "projects-grid";

    accessibleProjects.forEach(project => {
        const projectTasks = getProjectTasks(project.id);
        const done = projectTasks.filter(task => task.status === "done").length;
        const progress = projectTasks.length ? Math.round(done / projectTasks.length * 100) : 0;
        const admin = isProjectAdmin(project);
        const adminName = getNicknameById(project.adminId);
        const card = document.createElement("article");
        card.className = "project-card-large";
        card.innerHTML = `
            <div class="project-card-large-header">
                <h3>${escapeHTML(project.name)}</h3>
                <span class="project-role-badge ${admin ? "" : "member"}">${admin ? "Админ" : "Участник"}</span>
            </div>
            <p>${escapeHTML(project.description || "Без описания")}</p>
            <div class="project-card-meta-line">
                <span>Админ: @${escapeHTML(adminName)}</span>
                <span>Участников: ${(project.memberIds || []).length}</span>
                <span>Задач: ${projectTasks.length}${projectTaskCache.has(Number(project.id)) ? "" : " · откройте проект для загрузки"}</span>
            </div>
            <div class="project-progress">
                <div class="project-progress-top"><span>Прогресс</span><strong>${progress}%</strong></div>
                <div class="project-progress-track"><div class="project-progress-bar" style="width:${progress}%"></div></div>
            </div>
            <div class="project-card-large-footer">
                <span>${done} из ${projectTasks.length} выполнено</span>
                ${admin ? `
                    <div class="project-card-actions">
                        <button class="small-action edit-project" type="button">Управление</button>
                        <button class="small-action danger delete-project" type="button">Удалить</button>
                    </div>
                ` : ""}
            </div>
        `;

        card.addEventListener("click", () => selectProject(project.id));
        card.querySelector(".edit-project")?.addEventListener("click", event => {
            event.stopPropagation();
            openProjectModal(project.id);
        });
        card.querySelector(".delete-project")?.addEventListener("click", async event => {
            event.stopPropagation();
            try { await deleteProject(project.id); } catch (error) { showToast(getErrorMessage(error)); }
        });
        grid.appendChild(card);
        if (project.adminId) ensureUserCached(project.adminId).then(() => {});
    });

    elements.board.appendChild(grid);
}

function renderInvitationsPage() {
    elements.board.className = "board single-view";
    elements.board.innerHTML = "";

    if (!invitations.length) {
        renderEmptyState("Нет приглашений", "Новые приглашения в проекты появятся здесь.");
        return;
    }

    const list = document.createElement("div");
    list.className = "page-list";

    invitations.forEach(invitation => {
        const card = document.createElement("article");
        card.className = "page-task-card";
        card.innerHTML = `
            <div class="page-task-main">
                <div class="page-task-title">
                    <span class="role-badge">Приглашение</span>
                    <strong>${escapeHTML(invitation.projectName)}</strong>
                </div>
                <div class="page-task-meta">
                    <span>${escapeHTML(invitation.message || "Вас приглашают в проект")}</span>
                    ${invitation.createdAt ? `<span>${escapeHTML(new Date(invitation.createdAt).toLocaleString("ru-RU"))}</span>` : ""}
                </div>
            </div>
            <div class="page-task-actions">
                <button class="small-action accept-invitation" type="button">Принять</button>
                <button class="small-action danger decline-invitation" type="button">Отклонить</button>
                <button class="small-action delete-invitation" type="button">Удалить</button>
            </div>
        `;

        card.querySelector(".accept-invitation").addEventListener("click", async event => {
            event.stopPropagation();
            try { await respondInvitation(invitation.id, "accepted"); } catch (error) { showToast(getErrorMessage(error)); }
        });
        card.querySelector(".decline-invitation").addEventListener("click", async event => {
            event.stopPropagation();
            try { await respondInvitation(invitation.id, "declined"); } catch (error) { showToast(getErrorMessage(error)); }
        });
        card.querySelector(".delete-invitation").addEventListener("click", async event => {
            event.stopPropagation();
            try { await deleteInvitation(invitation.id); } catch (error) { showToast(getErrorMessage(error)); }
        });

        list.appendChild(card);
    });

    elements.board.appendChild(list);
}

async function respondInvitation(invitationId, action) {
    await api("PATCH", `/invitations/${Number(invitationId)}`, { action });
    await Promise.all([loadInvitations(), loadWorkspaceFromServer()]);
    if (action === "accepted") showToast("✓ Приглашение принято");
    else showToast("Приглашение отклонено");
    render();
}

async function deleteInvitation(invitationId) {
    await api("DELETE", `/invitations/${Number(invitationId)}`);
    invitations = invitations.filter(item => Number(item.id) !== Number(invitationId));
    renderInvitationsSidebar();
    render();
    showToast("Приглашение удалено");
}

async function renderSettingsPage() {
    elements.board.className = "board single-view";
    elements.board.innerHTML = `
        <div class="settings-panel">
            <section class="settings-section">
                <h3>Профиль</h3>
                <div class="settings-grid">
                    <label>
                        <span>Ник</span>
                        <input id="settingsUserName" type="text" minlength="3" maxlength="30">
                    </label>
                    <label>
                        <span>E-mail аккаунта</span>
                        <input id="settingsUserEmail" type="email" maxlength="160">
                    </label>
                    <label>
                        <span>Дата регистрации</span>
                        <input id="settingsRegistrationDate" type="text" disabled>
                    </label>
                    <label>
                        <span>Новый пароль</span>
                        <input id="settingsPassword" type="password" minlength="6" maxlength="128" placeholder="Оставьте пустым без изменения">
                    </label>
                    <label>
                        <span>Тема</span>
                        <select id="settingsTheme">
                            <option value="light">Светлая</option>
                            <option value="dark">Тёмная</option>
                            <option value="system">Системная</option>
                        </select>
                    </label>
                </div>
                <div class="settings-actions" style="margin-top:12px">
                    <button id="saveSettingsButton" class="small-action" type="button">Сохранить настройки</button>
                </div>
            </section>
            <section class="settings-section">
                <h3>Серверные данные</h3>
                <div class="settings-actions">
                    <button id="refreshWorkspaceButton" class="small-action" type="button">Обновить данные</button>
                </div>
            </section>
        </div>
    `;

    document.getElementById("settingsUserName").value = user.nickname || user.name;
    document.getElementById("settingsUserEmail").value = user.email;
    document.getElementById("settingsRegistrationDate").value = currentUser?.createdAt
        ? new Date(currentUser.createdAt).toLocaleString("ru-RU")
        : "—";
    document.getElementById("settingsTheme").value = settings.theme;

    document.getElementById("saveSettingsButton").addEventListener("click", async event => {
        const button = event.currentTarget;
        button.disabled = true;
        try {
            const nickname = cleanNickname(document.getElementById("settingsUserName").value);
            const email = document.getElementById("settingsUserEmail").value.trim();
            const password = document.getElementById("settingsPassword").value;

            validateNickname(nickname);
            if (email && !email.includes("@")) throw new Error("Введите корректный e-mail.");

            if (nickname !== currentUser.username) {
                const profile = await api("PUT", "/profile/username", { username: nickname });
                mapProfileFromServer(profile?.user_id ? profile : { ...currentUser, username: nickname });
            }

            if (email && email !== currentUser.email) {
                const profile = await api("PUT", "/profile/email", { email });
                mapProfileFromServer(profile?.user_id ? profile : { ...currentUser, email });
            }

            if (password) {
                await api("PATCH", "/profile/password", { password });
            }

            settings.theme = document.getElementById("settingsTheme").value;
            saveSettings();
            applyTheme();
            renderUser();
            renderProjectsSidebar();
            showToast("✓ Настройки сохранены");
        } catch (error) {
            showToast(getErrorMessage(error));
        } finally {
            button.disabled = false;
        }
    });

    document.getElementById("refreshWorkspaceButton").addEventListener("click", async event => {
        const button = event.currentTarget;
        button.disabled = true;
        try {
            await loadWorkspaceFromServer();
            await loadInvitations();
            render();
            showToast("✓ Данные обновлены");
        } catch (error) {
            showToast(getErrorMessage(error));
        } finally {
            button.disabled = false;
        }
    });
}

function renderEmptyState(title, text, buttonText = "", onClick = null) {
    elements.board.className = "board single-view";
    elements.board.innerHTML = "";
    const state = document.createElement("div");
    state.className = "empty-state";
    state.innerHTML = `
        <strong>${escapeHTML(title)}</strong>
        <p>${escapeHTML(text)}</p>
        ${buttonText ? `<button type="button">${escapeHTML(buttonText)}</button>` : ""}
    `;
    if (buttonText && onClick) state.querySelector("button").addEventListener("click", onClick);
    elements.board.appendChild(state);
}

function setPage(page) {
    if (!["overview", "my-tasks", "favorites", "projects", "settings", "invitations"].includes(page)) return;
    currentPage = page;
    closeAllFloatingMenus();
    saveSettings();

    if (page === "invitations") {
        loadInvitations()
            .then(render)
            .catch(error => showToast(getErrorMessage(error)));
    } else {
        render();
    }
}

function renderNavigation() {
    document.querySelectorAll("[data-page]").forEach(item => {
        item.classList.toggle("active", item.dataset.page === currentPage);
    });
    elements.projectsPageButton.classList.toggle("active", currentPage === "projects");
    renderInvitationsSidebar();
}

function renderPageHeader() {
    const project = getCurrentProject();
    const accessibleProjects = getAccessibleProjects();
    const adminProjects = getAdminProjects();

    elements.createTaskButton.classList.remove("hidden");
    elements.toolbar.classList.remove("hidden");
    elements.views.classList.remove("hidden");
    elements.breadcrumb.classList.remove("hidden");
    elements.createTaskButtonText.textContent = "Новая задача";

    if (currentPage === "overview") {
        if (!project) {
            elements.projectTitle.textContent = "Нет доступных проектов";
            elements.projectDescription.textContent = "Создайте проект или попросите администратора добавить вас в существующий.";
            elements.breadcrumbProject.textContent = "Проект";
        } else {
            const role = isProjectAdmin(project) ? "Администратор" : "Участник";
            elements.projectTitle.textContent = project.name;
            elements.projectDescription.textContent = `${project.description || "Задачи этого проекта"} · ${role}`;
            elements.breadcrumbProject.textContent = project.name;
        }
        elements.createTaskButton.classList.toggle("hidden", !project || !isProjectAdmin(project));
        return;
    }

    if (currentPage === "my-tasks") {
        const myTasksCount = tasks.filter(task => Number(task.assigneeId) === Number(currentUser?.id) && Boolean(getProject(task.projectId))).length;
        elements.breadcrumb.classList.add("hidden");
        elements.projectTitle.textContent = "Мои задачи";
        elements.projectDescription.textContent = `Назначено вам: ${myTasksCount}`;
        elements.views.classList.add("hidden");
        elements.createTaskButton.classList.toggle("hidden", adminProjects.length === 0);
        return;
    }

    if (currentPage === "favorites") {
        elements.breadcrumb.classList.add("hidden");
        elements.projectTitle.textContent = "Избранное";
        elements.projectDescription.textContent = "Отмеченные задачи из доступных вам проектов";
        elements.views.classList.add("hidden");
        elements.createTaskButton.classList.add("hidden");
        return;
    }

    if (currentPage === "projects") {
        elements.breadcrumb.classList.add("hidden");
        elements.projectTitle.textContent = "Мои проекты";
        elements.projectDescription.textContent = `Доступно проектов: ${accessibleProjects.length} · администратор: ${adminProjects.length}`;
        elements.toolbar.classList.add("hidden");
        elements.createTaskButton.classList.remove("hidden");
        elements.createTaskButtonText.textContent = "Новый проект";
        return;
    }

    if (currentPage === "invitations") {
        elements.breadcrumb.classList.add("hidden");
        elements.projectTitle.textContent = "Входящие приглашения";
        elements.projectDescription.textContent = invitations.length ? `Новых приглашений: ${invitations.length}` : "Новых приглашений нет";
        elements.toolbar.classList.add("hidden");
        elements.createTaskButton.classList.add("hidden");
        return;
    }

    elements.breadcrumb.classList.add("hidden");
    elements.projectTitle.textContent = "Настройки";
    elements.projectDescription.textContent = "Профиль, внешний вид и серверные данные";
    elements.toolbar.classList.add("hidden");
    elements.createTaskButton.classList.add("hidden");
}

function renderContent() {
    populateFilterProjects();
    syncFilterControls();

    if (currentPage === "overview") {
        if (currentView === "board") renderBoardView();
        else if (currentView === "list") renderTableView();
        else renderCalendarView();
        return;
    }

    if (currentPage === "my-tasks" || currentPage === "favorites") {
        renderTaskCollectionPage();
        return;
    }

    if (currentPage === "projects") {
        renderProjectsPage();
        return;
    }

    if (currentPage === "invitations") {
        renderInvitationsPage();
        return;
    }

    if (currentPage === "settings") renderSettingsPage();
}

function renderViewButtons() {
    document.querySelectorAll("[data-view]").forEach(button => {
        button.classList.toggle("active-view", button.dataset.view === currentView);
    });
}

function renderUser() {
    const nickname = user.nickname || user.name;
    const initials = getInitials(nickname);
    elements.sidebarUserName.textContent = `@${nickname}`;
    elements.sidebarUserEmail.textContent = user.email || "Мой аккаунт";
    elements.sidebarAvatar.textContent = initials;
    elements.topAvatar.textContent = initials;
}

function render() {
    validateCurrentProject();
    renderNavigation();
    renderProjectsSidebar();
    renderPageHeader();
    renderViewButtons();
    renderUser();
    renderContent();
}

function validateCurrentProject() {
    const accessibleProjects = getAccessibleProjects();
    if (currentProjectId && !getProject(currentProjectId)) {
        currentProjectId = accessibleProjects[0]?.id || null;
    }
    if (!currentProjectId && accessibleProjects.length) currentProjectId = accessibleProjects[0].id;
}

function populateTaskProjectSelect(selectedId = currentProjectId, adminOnly = true) {
    const source = adminOnly ? getAdminProjects() : getAccessibleProjects();
    elements.taskProjectInput.innerHTML = source.map(project =>
        `<option value="${project.id}">${escapeHTML(project.name)}</option>`
    ).join("");

    if (selectedId != null && source.some(project => Number(project.id) === Number(selectedId))) {
        elements.taskProjectInput.value = String(selectedId);
    }
}

function populateTaskAssigneeSelect(projectId, selectedId = "") {
    const project = getProject(projectId);
    const accounts = project ? getProjectAccounts(project.id) : [];
    elements.taskAssigneeInput.innerHTML =
        `<option value="">Не назначен</option>` +
        accounts.map(account => {
            const role = Number(account.id) === Number(project.adminId) ? "Админ" : "Участник";
            return `<option value="${escapeAttribute(account.id)}">@${escapeHTML(account.nickname || account.name)} — ${role}</option>`;
        }).join("");

    if (selectedId != null && accounts.some(account => Number(account.id) === Number(selectedId))) {
        elements.taskAssigneeInput.value = String(selectedId);
    } else {
        elements.taskAssigneeInput.value = "";
    }
}

function setTaskFormAccess(mode) {
    const fullEdit = mode === "admin" || mode === "create";
    const statusOnly = mode === "status";
    elements.taskForm.classList.toggle("form-readonly", !fullEdit);

    [
        elements.taskTitleInput,
        elements.taskDescriptionInput,
        elements.taskProjectInput,
        elements.taskAssigneeInput,
        elements.taskPriorityInput,
        elements.taskDateInput,
        elements.taskFavoriteInput
    ].forEach(control => control.disabled = !fullEdit);

    elements.taskStatusInput.disabled = !(fullEdit || statusOnly);
    elements.taskSubmitButton.classList.toggle("hidden", mode === "view");
}

function openTaskModal(status = "todo", taskId = null) {
    const adminProjects = getAdminProjects();
    if (!taskId && !adminProjects.length) {
        showToast("Создавать задачи может только администратор проекта");
        return;
    }

    closeAllFloatingMenus();
    elements.taskForm.reset();
    delete elements.taskForm.dataset.editingId;
    delete elements.taskForm.dataset.accessMode;
    elements.deleteTaskButton.classList.add("hidden");

    if (taskId) {
        const task = tasks.find(item => Number(item.id) === Number(taskId));
        if (!task || !getProject(task.projectId)) return;

        const admin = canManageTask(task);
        const statusOnly = !admin && Number(task.assigneeId) === Number(currentUser.id);
        const mode = admin ? "admin" : (statusOnly ? "status" : "view");

        elements.taskForm.dataset.editingId = String(task.id);
        elements.taskForm.dataset.accessMode = mode;
        elements.taskModalTitle.textContent = admin ? "Редактировать задачу" : "Задача";
        elements.taskModalSubtitle.textContent = admin
            ? "Измените параметры и назначьте исполнителя"
            : (statusOnly ? "Вы назначены исполнителем и можете изменить статус" : "Просмотр задачи проекта");
        elements.taskSubmitButton.textContent = admin ? "Сохранить" : "Сохранить статус";
        elements.deleteTaskButton.classList.toggle("hidden", !admin);

        populateTaskProjectSelect(task.projectId, admin);
        if (!Array.from(elements.taskProjectInput.options).some(option => Number(option.value) === Number(task.projectId))) {
            elements.taskProjectInput.innerHTML = `<option value="${task.projectId}">${escapeHTML(getProjectName(task.projectId))}</option>`;
        }
        elements.taskProjectInput.value = String(task.projectId);
        populateTaskAssigneeSelect(task.projectId, task.assigneeId);

        elements.taskTitleInput.value = task.title;
        elements.taskDescriptionInput.value = task.description;
        elements.taskStatusInput.value = task.status;
        elements.taskPriorityInput.value = task.priority;
        elements.taskDateInput.value = task.date || "";
        elements.taskFavoriteInput.checked = task.favorite;
        setTaskFormAccess(mode);
    } else {
        const selectedProject = getProject(currentProjectId);
        const projectId = selectedProject && isProjectAdmin(selectedProject)
            ? selectedProject.id
            : adminProjects[0].id;

        elements.taskForm.dataset.accessMode = "create";
        elements.taskModalTitle.textContent = "Новая задача";
        elements.taskModalSubtitle.textContent = "Создайте задачу и назначьте исполнителя из участников проекта";
        elements.taskSubmitButton.textContent = "Создать задачу";
        populateTaskProjectSelect(projectId, true);
        elements.taskProjectInput.value = String(projectId);
        populateTaskAssigneeSelect(projectId, "");
        elements.taskStatusInput.value = status;
        elements.taskPriorityInput.value = "medium";
        elements.taskFavoriteInput.checked = false;
        setTaskFormAccess("create");
    }

    elements.taskModal.classList.remove("hidden");
    setTimeout(() => {
        if (!elements.taskTitleInput.disabled) elements.taskTitleInput.focus();
    }, 30);
}

function closeTaskModal() {
    elements.taskModal.classList.add("hidden");
    elements.taskForm.reset();
    elements.taskForm.classList.remove("form-readonly");
    [
        elements.taskTitleInput,
        elements.taskDescriptionInput,
        elements.taskProjectInput,
        elements.taskAssigneeInput,
        elements.taskStatusInput,
        elements.taskPriorityInput,
        elements.taskDateInput,
        elements.taskFavoriteInput
    ].forEach(control => control.disabled = false);
    delete elements.taskForm.dataset.editingId;
    delete elements.taskForm.dataset.accessMode;
}

function addInviteButtonToProjectModal(project) {
    let button = document.getElementById("inviteProjectButton");
    if (!button) {
        button = document.createElement("button");
        button.id = "inviteProjectButton";
        button.className = "small-action";
        button.type = "button";
        button.textContent = "Пригласить";
        elements.projectMembersSection.querySelector(".project-members-heading")?.appendChild(button);
    }

    button.classList.toggle("hidden", !project || !isProjectAdmin(project));
    button.onclick = () => {
        elements.projectMemberSearch.focus();
        showToast("Найдите пользователя по нику и нажмите «Пригласить».");
    };
}

function openProjectModal(projectId = null) {
    closeAllFloatingMenus();
    elements.projectForm.reset();
    delete elements.projectForm.dataset.editingId;
    elements.deleteProjectButton.classList.add("hidden");
    elements.projectMembersSection.classList.add("hidden");
    elements.projectMemberSearchResults.innerHTML = "";
    elements.projectMemberSearch.value = "";

    if (projectId) {
        const project = getProject(projectId);
        if (!project) return;
        if (!isProjectAdmin(project)) {
            showToast("Управление участниками доступно только администратору");
            return;
        }

        elements.projectForm.dataset.editingId = String(project.id);
        elements.projectModalTitle.textContent = "Управление проектом";
        elements.projectModalSubtitle.textContent = "Название, описание, роли и участники проекта";
        elements.projectSubmitButton.textContent = "Сохранить";
        elements.deleteProjectButton.classList.remove("hidden");
        elements.projectNameInput.value = project.name;
        elements.projectDescriptionInput.value = project.description;
        renderProjectMembers(project.id);
        addInviteButtonToProjectModal(project);
    } else {
        elements.projectModalTitle.textContent = "Новый проект";
        elements.projectModalSubtitle.textContent = "После создания вы автоматически станете администратором";
        elements.projectSubmitButton.textContent = "Создать проект";
    }

    elements.projectModal.classList.remove("hidden");
    setTimeout(() => elements.projectNameInput.focus(), 30);
}

function closeProjectModal() {
    elements.projectModal.classList.add("hidden");
    elements.projectForm.reset();
    elements.projectMembersSection.classList.add("hidden");
    elements.projectMemberSearchResults.innerHTML = "";
    elements.projectMemberSearch.value = "";
    delete elements.projectForm.dataset.editingId;
}

function openTaskMenu(taskId, button) {
    currentTaskMenuId = Number(taskId);
    const task = tasks.find(item => Number(item.id) === Number(taskId));
    if (!task || !getProject(task.projectId)) return;

    closeAllFloatingMenus();
    currentTaskMenuId = Number(taskId);

    const favoriteAction = elements.taskMenu.querySelector('[data-action="favorite"]');
    const editAction = elements.taskMenu.querySelector('[data-action="edit"]');
    const deleteAction = elements.taskMenu.querySelector('[data-action="delete"]');
    const canManage = canManageTask(task);
    const canStatus = canChangeTaskStatus(task);

    favoriteAction.textContent = task.favorite ? "☆ Убрать из избранного" : "★ В избранное";
    editAction.textContent = canManage ? "✎ Редактировать" : "👁 Открыть";
    favoriteAction.classList.toggle("hidden", !canManage);
    deleteAction.classList.toggle("hidden", !canManage);

    elements.taskMenu.querySelectorAll('[data-action="todo"], [data-action="progress"], [data-action="done"]')
        .forEach(buttonItem => buttonItem.classList.toggle("hidden", !canStatus));

    positionFloatingMenu(elements.taskMenu, button, 190);
}

function closeTaskMenu() {
    currentTaskMenuId = null;
    elements.taskMenu.classList.add("hidden");
}

function applyTheme() {
    let dark = settings.theme === "dark";
    if (settings.theme === "system") {
        dark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    }
    document.body.classList.toggle("theme-dark", dark);
}

function setAuthMessage(message = "", success = false) {
    elements.authMessage.textContent = message;
    elements.authMessage.classList.toggle("success", success);
}

function setAuthMode(mode) {
    authMode = mode === "register" ? "register" : "login";
    const registering = authMode === "register";

    elements.loginTab.classList.toggle("active", !registering);
    elements.registerTab.classList.toggle("active", registering);
    elements.authNameField.classList.toggle("hidden", !registering);
    elements.authConfirmField.classList.toggle("hidden", !registering);
    elements.authNameInput.required = registering;
    elements.authConfirmInput.required = registering;
    elements.authPasswordInput.autocomplete = registering ? "new-password" : "current-password";
    elements.authLoginLabel.textContent = registering ? "E-mail" : "Ник или e-mail";
    elements.authEmailInput.type = registering ? "email" : "text";
    elements.authEmailInput.autocomplete = registering ? "email" : "username";
    elements.authEmailInput.placeholder = registering ? "name@example.com" : "@nickname или name@example.com";
    elements.authSubmitButton.textContent = registering ? "Создать аккаунт" : "Войти";
    setAuthMessage();
}

function showAuthScreen(mode = "login") {
    elements.app.classList.add("hidden");
    elements.authScreen.classList.remove("hidden");
    elements.authForm.reset();
    setAuthMode(mode);
    setTimeout(() => elements.authEmailInput.focus(), 30);
}

async function enterAccount(profile) {
    mapProfileFromServer(profile);
    settings = loadSettings();

    const savedPage = localStorage.getItem(userStorageKey(STORAGE.currentPage));
    const savedView = localStorage.getItem(userStorageKey(STORAGE.currentView));
    const savedProject = localStorage.getItem(userStorageKey(STORAGE.currentProject));

    currentPage = ["overview", "my-tasks", "favorites", "projects", "settings", "invitations"].includes(savedPage)
        ? savedPage : "overview";
    currentView = ["board", "list", "calendar"].includes(savedView) ? savedView : "board";
    currentProjectId = savedProject ? Number(savedProject) : null;

    await loadWorkspaceFromServer();
    await loadInvitations();

    if (!getAccessibleProjects().some(project => Number(project.id) === Number(currentProjectId))) {
        currentProjectId = getAccessibleProjects()[0]?.id || null;
    }

    elements.authScreen.classList.add("hidden");
    elements.app.classList.remove("hidden");
    elements.searchInput.value = "";
    resetFilters(false);
    applyTheme();
    saveSettings();
    render();

    if (currentPage === "overview" && currentProjectId) {
        try { await loadProjectDetails(currentProjectId); } catch (error) { showToast(getErrorMessage(error)); }
    }
}

async function registerAccount() {
    const nickname = cleanNickname(elements.authNameInput.value);
    const email = elements.authEmailInput.value.trim();
    const password = elements.authPasswordInput.value;
    const confirmPassword = elements.authConfirmInput.value;

    if (!nickname) throw new Error("Введите ник.");
    validateNickname(nickname);
    if (!email) throw new Error("Введите e-mail.");
    if (password.length < 6) throw new Error("Пароль должен содержать минимум 6 символов.");
    if (password !== confirmPassword) throw new Error("Пароли не совпадают.");

    await api("POST", "/auth/register", {
        username: nickname,
        email,
        password
    });

    const login = await api("POST", "/auth/login", {
        username_or_email: nickname,
        password
    });

    if (!login?.access_token) throw new Error("Сервер не вернул токен.");
    setToken(login.access_token);

    const profile = await api("GET", "/profile");
    await enterAccount(profile);
    showToast("✓ Аккаунт создан");
}

async function signInAccount() {
    const identifier = elements.authEmailInput.value.trim();
    const password = elements.authPasswordInput.value;
    if (!identifier) throw new Error("Введите ник или e-mail.");

    const result = await api("POST", "/auth/login", {
        username_or_email: identifier,
        password
    });

    if (!result?.access_token) throw new Error("Сервер не вернул токен.");
    setToken(result.access_token);

    const profile = await api("GET", "/profile");
    await enterAccount(profile);
}

function signOutAccount() {
    clearToken();
    clearLocalWorkspace();
    settings = { ...DEFAULT_SETTINGS };
    user = { ...DEFAULT_USER };
    closeTaskModal();
    closeProjectModal();
    closeAllFloatingMenus();
    showAuthScreen("login");
}

async function initializeAuth() {
    const token = getToken();
    if (!token) {
        showAuthScreen("login");
        return;
    }

    try {
        const profile = await api("GET", "/profile");
        await enterAccount(profile);
    } catch (error) {
        clearToken();
        clearLocalWorkspace();
        showAuthScreen("login");
    }
}

elements.loginTab.addEventListener("click", () => setAuthMode("login"));
elements.registerTab.addEventListener("click", () => setAuthMode("register"));

elements.authForm.addEventListener("submit", async event => {
    event.preventDefault();
    if (elements.authSubmitButton.disabled) return;

    setAuthMessage();
    elements.authSubmitButton.disabled = true;
    try {
        if (authMode === "register") await registerAccount();
        else await signInAccount();
    } catch (error) {
        setAuthMessage(getErrorMessage(error));
    } finally {
        elements.authSubmitButton.disabled = false;
    }
});

elements.logoutButton.addEventListener("click", signOutAccount);

document.querySelectorAll("[data-page]").forEach(item => {
    item.addEventListener("click", event => {
        event.preventDefault();
        setPage(item.dataset.page);
    });
});

elements.projectsPageButton.addEventListener("click", () => setPage("projects"));

elements.addProjectButton.addEventListener("click", () => openProjectModal());

elements.createTaskButton.addEventListener("click", () => {
    if (currentPage === "projects") openProjectModal();
    else openTaskModal();
});

document.querySelectorAll("[data-view]").forEach(button => {
    button.addEventListener("click", () => {
        currentView = button.dataset.view;
        saveSettings();
        renderViewButtons();
        renderContent();
    });
});

elements.closeTaskModal.addEventListener("click", closeTaskModal);
elements.cancelTaskButton.addEventListener("click", closeTaskModal);
elements.closeProjectModal.addEventListener("click", closeProjectModal);
elements.cancelProjectButton.addEventListener("click", closeProjectModal);

elements.taskProjectInput.addEventListener("change", () => {
    populateTaskAssigneeSelect(elements.taskProjectInput.value, "");
});

let memberSearchTimer = null;
elements.projectMemberSearch.addEventListener("input", () => {
    const projectId = elements.projectForm.dataset.editingId;
    if (!projectId) return;
    clearTimeout(memberSearchTimer);
    memberSearchTimer = setTimeout(() => {
        renderProjectMemberSearchResults(projectId, elements.projectMemberSearch.value);
    }, 250);
});

elements.taskForm.addEventListener("submit", async event => {
    event.preventDefault();
    if (elements.taskSubmitButton.disabled) return;

    const editingId = elements.taskForm.dataset.editingId;
    const accessMode = elements.taskForm.dataset.accessMode;

    if (editingId && accessMode === "view") return;

    elements.taskSubmitButton.disabled = true;
    try {
        if (editingId && accessMode === "status") {
            await changeTaskStatus(editingId, elements.taskStatusInput.value);
            closeTaskModal();
            return;
        }

        const title = elements.taskTitleInput.value.trim();
        if (!title) throw new Error("Введите название задачи.");

        const data = {
            title,
            description: elements.taskDescriptionInput.value.trim(),
            projectId: Number(elements.taskProjectInput.value),
            assigneeId: elements.taskAssigneeInput.value ? Number(elements.taskAssigneeInput.value) : null,
            status: elements.taskStatusInput.value,
            priority: elements.taskPriorityInput.value,
            date: elements.taskDateInput.value || null,
            favorite: elements.taskFavoriteInput.checked
        };

        if (editingId) await updateTask(Number(editingId), data);
        else await createTask(data);

        closeTaskModal();
    } catch (error) {
        showToast(getErrorMessage(error));
    } finally {
        elements.taskSubmitButton.disabled = false;
    }
});

elements.deleteTaskButton.addEventListener("click", async () => {
    if (elements.deleteTaskButton.disabled) return;
    const taskId = elements.taskForm.dataset.editingId;
    if (!taskId) return;

    elements.deleteTaskButton.disabled = true;
    try {
        await deleteTask(Number(taskId));
    } catch (error) {
        showToast(getErrorMessage(error));
    } finally {
        elements.deleteTaskButton.disabled = false;
    }
});

elements.projectForm.addEventListener("submit", async event => {
    event.preventDefault();
    if (elements.projectSubmitButton.disabled) return;

    const name = elements.projectNameInput.value.trim();
    if (!name) return;

    const description = elements.projectDescriptionInput.value.trim();
    const editingId = elements.projectForm.dataset.editingId;
    elements.projectSubmitButton.disabled = true;

    try {
        if (editingId) await updateProject(Number(editingId), name, description);
        else await createProject(name, description);
        closeProjectModal();
    } catch (error) {
        showToast(getErrorMessage(error));
    } finally {
        elements.projectSubmitButton.disabled = false;
    }
});

elements.deleteProjectButton.addEventListener("click", async () => {
    if (elements.deleteProjectButton.disabled) return;
    const projectId = elements.projectForm.dataset.editingId;
    if (!projectId) return;

    elements.deleteProjectButton.disabled = true;
    try {
        await deleteProject(Number(projectId));
    } catch (error) {
        showToast(getErrorMessage(error));
    } finally {
        elements.deleteProjectButton.disabled = false;
    }
});

elements.searchInput.addEventListener("input", () => {
    if (["overview", "my-tasks", "favorites"].includes(currentPage)) renderContent();
});

elements.filterButton.addEventListener("click", event => {
    event.stopPropagation();
    const willOpen = elements.filterMenu.classList.contains("hidden");
    closeAllFloatingMenus();
    if (willOpen) positionFloatingMenu(elements.filterMenu, elements.filterButton);
});

elements.sortButton.addEventListener("click", event => {
    event.stopPropagation();
    const willOpen = elements.sortMenu.classList.contains("hidden");
    closeAllFloatingMenus();
    if (willOpen) positionFloatingMenu(elements.sortMenu, elements.sortButton);
});

elements.filterStatus.addEventListener("change", () => {
    filters.status = elements.filterStatus.value;
    renderContent();
});

elements.filterPriority.addEventListener("change", () => {
    filters.priority = elements.filterPriority.value;
    renderContent();
});

elements.filterProject.addEventListener("change", () => {
    filters.project = elements.filterProject.value;
    renderContent();
});

elements.filterOverdue.addEventListener("change", () => {
    filters.overdue = elements.filterOverdue.checked;
    renderContent();
});

elements.resetFiltersButton.addEventListener("click", resetFilters);

elements.sortSelect.addEventListener("change", () => {
    settings.sort = elements.sortSelect.value;
    saveSettings();
    renderContent();
});

elements.taskMenu.querySelectorAll("button").forEach(button => {
    button.addEventListener("click", async () => {
        const taskId = currentTaskMenuId;
        if (taskId == null) return;
        const action = button.dataset.action;

        try {
            if (action === "edit") openTaskModal("todo", taskId);
            else if (action === "favorite") await toggleFavorite(taskId);
            else if (action === "delete") await deleteTask(taskId);
            else if (STATUS[action]) await changeTaskStatus(taskId, action);
        } catch (error) {
            showToast(getErrorMessage(error));
        }
    });
});

document.addEventListener("click", event => {
    if (!elements.taskMenu.contains(event.target)) closeTaskMenu();
    if (!elements.filterMenu.contains(event.target) && event.target !== elements.filterButton) {
        elements.filterMenu.classList.add("hidden");
    }
    if (!elements.sortMenu.contains(event.target) && event.target !== elements.sortButton) {
        elements.sortMenu.classList.add("hidden");
    }
});

elements.taskModal.addEventListener("click", event => {
    if (event.target === elements.taskModal) closeTaskModal();
});

elements.projectModal.addEventListener("click", event => {
    if (event.target === elements.projectModal) closeProjectModal();
});

document.addEventListener("keydown", event => {
    if (event.key === "Escape") {
        closeTaskModal();
        closeProjectModal();
        closeAllFloatingMenus();
    }

    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        elements.searchInput.focus();
    }
});

elements.helpButton.addEventListener("click", () => {
    alert("Tasker: создавайте проекты и задачи, перетаскивайте карточки между колонками и используйте Ctrl+K для поиска.");
});

elements.notificationButton.addEventListener("click", async () => {
    try {
        await loadInvitations();
        if (invitations.length) {
            setPage("invitations");
        } else {
            const overdue = tasks.filter(task =>
                Number(task.assigneeId) === Number(currentUser?.id) &&
                Boolean(getProject(task.projectId)) &&
                isOverdue(task)
            ).length;
            alert(overdue ? `Ваших просроченных задач: ${overdue}` : "У вас нет новых приглашений и просроченных задач.");
        }
    } catch (error) {
        showToast(getErrorMessage(error));
    }
});

if (window.matchMedia) {
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener?.("change", () => {
        if (settings.theme === "system") applyTheme();
    });
}

window.addEventListener("tasker:unauthorized", () => {
    clearLocalWorkspace();
    currentUser = null;
    settings = { ...DEFAULT_SETTINGS };
    user = { ...DEFAULT_USER };
    closeTaskModal();
    closeProjectModal();
    showAuthScreen("login");
    showToast("Сессия истекла. Войдите снова.");
});

setAuthMode("login");
initializeAuth();
