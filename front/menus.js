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