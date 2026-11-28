// Файл для управления приглашениями пользователей в проекты

// Загрузка входящих приглашений с сервера
let incomingInvitationVersion = 0;
async function loadInvitations() {
    const generation = sessionGeneration, version = ++incomingInvitationVersion;
    const items = await apiAll("/invitations?status_invited=pending");
    assertSession(generation);
    if (version !== incomingInvitationVersion) return;
    invitations = items.filter(item => item.status_invited === "pending").map(mapInvitation);
    renderInvitationsSidebar();
}

// Создание пункта меню для приглашений, если его нет
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

// Отрисовка счетчика приглашений в боковом меню
function renderInvitationsSidebar() {
    const nav = ensureInvitationNav();
    nav.classList.toggle("active", currentPage === "invitations");
    const count = nav.querySelector(".invitation-count");
    if (count) count.textContent = invitations.length ? String(invitations.length) : "";
}

// Отрисовка отправленных приглашений в модальном окне проекта
let invitationRenderVersion = 0;
async function renderProjectInvitations(projectId) {
    const version = ++invitationRenderVersion;
    const generation = sessionGeneration;
    const isCurrent = () => generation === sessionGeneration && version === invitationRenderVersion && Number(elements.projectForm.dataset.editingId) === Number(projectId);
    const project = getProject(projectId);
    if (!project || !canManageProject(project)) return;

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
        const list = (await apiAll(`/invitations/project/${Number(projectId)}?status_invited=pending`)).filter(item => item.status_invited === "pending");
        if (!isCurrent()) return;

        if (!list.length) {
            section.insertAdjacentHTML("beforeend", `<div class="member-search-empty">Нет активных приглашений.</div>`);
            return;
        }

        list.forEach(raw => {
            const invitation = mapInvitation(raw);
            const recipientId = raw?.user_id ?? raw?.recipient_id ?? raw?.invitee_id;
            const recipientName = raw?.invitee_username || raw?.username || raw?.recipient_username || (recipientId ? getNicknameById(recipientId) : "Пользователь");
            if (recipientId && (raw?.invitee_username || raw?.username || raw?.recipient_username)) userCache.set(Number(recipientId), cleanNickname(recipientName));

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

            row.querySelector(".member-remove-button").addEventListener("click", async event => {
                const button = event.currentTarget;
                if (button.disabled) return;
                button.disabled = true;
                try {
                    if (await deleteInvitation(invitation.id) && isCurrent()) await renderProjectInvitations(projectId);
                } catch (error) {
                    showToast(getErrorMessage(error));
                } finally { button.disabled = false; }
            });

            section.appendChild(row);
        });
    } catch (error) {
        if (isCurrent()) section.insertAdjacentHTML("beforeend", `<div class="member-search-empty">${escapeHTML(getErrorMessage(error))}</div>`);
    }
}

// Отрисовка страницы с приглашениями
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

        list.appendChild(card);
    });

    elements.board.appendChild(list);
}

// Ответ на приглашение (принять или отклонить)
async function respondInvitation(invitationId, action) {
    if (!["accepted", "declined"].includes(action)) return false;
    return withWriteLock(`invitation:${Number(invitationId)}`, async generation => {
        await api("PATCH", `/invitations/${Number(invitationId)}`, { action });
        assertSession(generation); incomingInvitationVersion++;
        invitations = invitations.filter(item => item.id !== Number(invitationId));
        render(); showToast(action === "accepted" ? "✓ Приглашение принято" : "Приглашение отклонено");
        if (action === "accepted") {
            try { await loadWorkspaceFromServer(); assertSession(generation); render(); }
            catch (error) { if (generation === sessionGeneration) showToast("Приглашение принято. Обновите данные для отображения проекта."); }
        }
        return true;
    });
}

async function deleteInvitation(invitationId) {
    return withWriteLock(`invitation:${Number(invitationId)}`, async generation => {
        await api("DELETE", `/invitations/${Number(invitationId)}`);
        assertSession(generation); incomingInvitationVersion++;
        invitations = invitations.filter(item => item.id !== Number(invitationId));
        renderInvitationsSidebar(); showToast("Приглашение отменено"); return true;
    });
}
