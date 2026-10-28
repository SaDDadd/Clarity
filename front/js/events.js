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