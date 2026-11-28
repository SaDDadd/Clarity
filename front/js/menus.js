// Файл для управления всплывающими контекстными меню

// Закрытие всех открытых меню
function closeAllFloatingMenus() {
    closeTaskMenu();
    elements.filterMenu.classList.add("hidden");
    elements.sortMenu.classList.add("hidden");
}

// Позиционирование плавающего меню относительно кнопки
function positionFloatingMenu(menu, button, width = 230) {
    const rect = button.getBoundingClientRect();
    menu.classList.remove("hidden");
    width = Math.min(width, Math.max(0, window.innerWidth - 20));
    menu.style.maxWidth = `${width}px`;
    menu.style.maxHeight = `${Math.max(0, window.innerHeight - 20)}px`;
    menu.style.overflowY = "auto";
    let left = rect.right - width;
    let top = rect.bottom + 7;
    if (left < 10) left = 10;
    if (left + width > window.innerWidth - 10) left = window.innerWidth - width - 10;
    if (top + menu.offsetHeight > window.innerHeight - 10) top = rect.top - menu.offsetHeight - 7;
    menu.style.left = `${Math.max(10, left)}px`;
    menu.style.top = `${Math.max(10, top)}px`;
}

// Открытие контекстного меню для задачи
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
    editAction.textContent = canEditTask(task) ? "✎ Редактировать" : "👁 Открыть";
    favoriteAction.classList.toggle("hidden", !canEditTask(task));
    deleteAction.classList.toggle("hidden", !canManage);

    elements.taskMenu.querySelectorAll('[data-action="todo"], [data-action="progress"], [data-action="done"]')
        .forEach(buttonItem => buttonItem.classList.toggle("hidden", !canStatus));

    positionFloatingMenu(elements.taskMenu, button, 190);
}

// Закрытие меню задачи
function closeTaskMenu() {
    currentTaskMenuId = null;
    elements.taskMenu.classList.add("hidden");
}