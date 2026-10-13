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