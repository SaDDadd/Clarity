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