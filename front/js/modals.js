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