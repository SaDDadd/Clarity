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