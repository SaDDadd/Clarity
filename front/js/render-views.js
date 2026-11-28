let profileSaving = null;
// Файл для альтернативных представлений задач (список, календарь) и страницы проектов/настроек

// Создание карточки задачи для страницы списка задач
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
                <span class="assignee-label">Исполнитель: ${task.assigneeId ? `@${escapeHTML(assigneeName)}` : "не назначен"}</span>
                ${isOverdue(task) ? `<span style="color:var(--danger)">Просрочено</span>` : ""}
            </div>
        </div>
        <div class="page-task-actions">
            <button class="favorite-button ${task.favorite ? "active" : ""}" type="button" ${canEditTask(task) ? "" : "disabled"}>${task.favorite ? "★" : "☆"}</button>
            <button class="small-action edit-task" type="button">${canEditTask(task) ? "Редактировать" : "Открыть"}</button>
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
    bindTaskKeyboard(card, task.id);
    if (task.assigneeId) ensureUserCached(task.assigneeId).then(name => { if (name && card.isConnected) card.querySelector(".assignee-label").textContent = `Исполнитель: @${name}`; });
    return card;
}

// Отрисовка задач в виде таблицы
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
            <td class="assignee-label">${task.assigneeId ? `@${escapeHTML(getNicknameById(task.assigneeId))}` : "Не назначен"}</td>
            <td><span class="priority ${task.priority}">${PRIORITY[task.priority]}</span></td>
            <td style="${isOverdue(task) ? "color:var(--danger);font-weight:600;" : ""}">${task.date ? formatDate(task.date) : "Без срока"}</td>
            <td>${STATUS[task.status]}</td>
            <td class="star-cell"><button class="favorite-button ${task.favorite ? "active" : ""}" type="button" ${canEditTask(task) ? "" : "disabled"}>${task.favorite ? "★" : "☆"}</button></td>
        `;
        row.addEventListener("click", () => openTaskModal("todo", task.id));
        row.querySelector(".favorite-button").addEventListener("click", async event => {
            event.stopPropagation();
            try { await toggleFavorite(task.id); } catch (error) { showToast(getErrorMessage(error)); }
        });
        bindTaskKeyboard(row, task.id);
        if (task.assigneeId) ensureUserCached(task.assigneeId).then(name => { if (name && row.isConnected) row.querySelector(".assignee-label").textContent = `@${name}`; });
        tbody.appendChild(row);
    });
    elements.board.appendChild(wrap);
}

// Отрисовка задач в виде календаря
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

// Отрисовка страниц "Мои задачи" и "Избранное"
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

// Отрисовка страницы со всеми проектами пользователя
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
        const canManage = canManageProject(project);
        const adminName = getNicknameById(project.adminId);
        const card = document.createElement("article");
        card.className = "project-card-large";
        card.innerHTML = `
            <div class="project-card-large-header">
                <h3>${escapeHTML(project.name)}</h3>
                <span class="project-role-badge ${admin ? "" : (project.role === "curator" ? "curator" : "member")}">
                    ${admin ? "Админ" : (project.role === "curator" ? "Куратор" : "Участник")}
                </span>
            </div>
            <p>${escapeHTML(project.description || "Без описания")}</p>
            <div class="project-card-meta-line">
                <span class="project-admin-label">Админ: @${escapeHTML(adminName)}</span>
                <span>Участников: ${(project.memberIds || []).length + 1}</span>
                <span>Задач: ${projectTasks.length}${projectTaskCache.has(Number(project.id)) ? "" : " · откройте проект для загрузки"}</span>
            </div>
            <div class="project-progress">
                <div class="project-progress-top"><span>Прогресс</span><strong>${progress}%</strong></div>
                <div class="project-progress-track"><div class="project-progress-bar" style="width:${progress}%"></div></div>
            </div>
            <div class="project-card-large-footer">
                <span>${done} из ${projectTasks.length} выполнено</span>
                <div class="project-card-actions">
                    ${canManage ? '<button class="small-action edit-project" type="button">Управление</button>' : ""}
                    ${admin ? '<button class="small-action danger delete-project" type="button">Удалить</button>' : ""}
                    <button class="small-action leave-project" type="button">Выйти</button>
                </div>
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
        card.querySelector(".leave-project").addEventListener("click", async event => { event.stopPropagation(); await runButtonAction(event.currentTarget, () => leaveProject(project.id)); });
        grid.appendChild(card);
        if (project.adminId) ensureUserCached(project.adminId).then(name => { if (name && card.isConnected) card.querySelector(".project-admin-label").textContent = `Админ: @${name}`; });
    });

    elements.board.appendChild(grid);
}

// Отрисовка страницы настроек
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
                        <input id="settingsUserEmail" type="email" maxlength="100">
                    </label>
                    <label>
                        <span>Дата регистрации</span>
                        <input id="settingsRegistrationDate" type="text" disabled>
                    </label>
                    <label>
                        <span>Новый пароль</span>
                        <input id="settingsPassword" type="password" minlength="8" maxlength="50" placeholder="Оставьте пустым без изменения">
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
                    <button id="deleteAccountButton" class="small-action danger" type="button">Удалить аккаунт</button>
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

    // Обработчик сохранения настроек профиля
    document.getElementById("saveSettingsButton").addEventListener("click", async event => {
        const button = event.currentTarget;
        const generation = sessionGeneration;
        if (profileSaving === generation) return;
        profileSaving = generation;
        button.disabled = true;
        try {
            const nickname = cleanNickname(document.getElementById("settingsUserName").value);
            const email = document.getElementById("settingsUserEmail").value.trim();
            const password = document.getElementById("settingsPassword").value;
            const theme = document.getElementById("settingsTheme").value;

            validateNickname(nickname);
            if (!isValidEmail(email) || email.length > 100) throw new Error("Введите корректный e-mail.");

            if (password && (password.length < 8 || password.length > 50)) throw new Error("Пароль должен содержать от 8 до 50 символов.");

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

            assertSession(generation);
            settings.theme = theme;
            saveSettings();
            applyTheme();
            renderUser();
            renderProjectsSidebar();
            if (button.isConnected) document.getElementById("settingsPassword").value = "";
            showToast("✓ Настройки сохранены");
        } catch (error) {
            showToast(getErrorMessage(error));
        } finally {
            if (profileSaving === generation) profileSaving = null;
            button.disabled = false;
        }
    });

    document.getElementById("deleteAccountButton").addEventListener("click", async event => {
        const button = event.currentTarget;
        await runButtonAction(button, () => withWriteLock("profile", async generation => {
            if (!confirm("Безвозвратно удалить аккаунт? Сервер снимет ваши назначения и передаст или удалит проекты, которыми вы управляете.")) return false;
            await api("DELETE", "/profile");
            assertSession(generation); signOutAccount(); setAuthMessage("Аккаунт удалён", true); return true;
        }));
    });

    // Обработчик принудительного обновления данных с сервера
    document.getElementById("refreshWorkspaceButton").addEventListener("click", async event => {
        const button = event.currentTarget;
        const originalText = button.textContent;
        button.disabled = true;
        button.textContent = "Загрузка данных..";
        try {
            await loadWorkspaceFromServer();
            await loadInvitations();
            render();
            showToast("✓ Данные обновлены");
        } catch (error) {
            showToast(getErrorMessage(error));
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    });
}