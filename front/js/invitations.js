async function loadInvitations() {
    const result = await api("GET", "/invitations");
    invitations = (Array.isArray(result) ? result : []).map(mapInvitation);
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