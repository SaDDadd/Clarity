// Файл для отрисовки списка проектов в левом боковом меню

// Отрисовка проектов в сайдбаре
function renderProjectsSidebar() {
    elements.projectsList.innerHTML = "";

    getAccessibleProjects().forEach(project => {
        const admin = isProjectAdmin(project);
        const canManage = canManageProject(project);
        const item = document.createElement("div");
        item.className = "project";
        if (currentPage === "overview" && Number(project.id) === Number(currentProjectId)) {
            item.classList.add("active-project");
        }

        // Определение текста и стиля бейджа роли
        let badgeText = "У";
        let badgeClass = "member";
        if (admin) {
        badgeText = "A";
        badgeClass = "";
        } else if (project.role === "curator") {
            badgeText = "К";
            badgeClass = "curator";
        }

        item.innerHTML = `
            <a class="project-link" href="#project-${project.id}">
                <span class="project-dot purple"></span>
                <span class="project-name">${escapeHTML(project.name)}</span>
                <span class="project-role-badge ${badgeClass}">${badgeText}</span>
            </a>
            ${canManage ? `
                <span class="project-actions">
                    <button class="project-edit" type="button" aria-label="Редактировать проект">✎</button>
                    ${admin ? '<button class="project-delete" type="button" aria-label="Удалить проект">×</button>' : ""}
                </span>
            ` : ""}
        `;

        item.querySelector(".project-link").addEventListener("click", event => {
            event.preventDefault();
            if (event.target.closest(".project-edit") || event.target.closest(".project-delete")) return;
            selectProject(project.id);
        });

        item.querySelector(".project-edit")?.addEventListener("click", event => {
            event.preventDefault();
            event.stopPropagation();
            openProjectModal(project.id);
        });

        item.querySelector(".project-delete")?.addEventListener("click", async event => {
            event.preventDefault();
            event.stopPropagation();
            try {
                await deleteProject(project.id);
            } catch (error) {
                showToast(getErrorMessage(error));
            }
        });

        elements.projectsList.appendChild(item);
    });

    renderInvitationsSidebar();
}