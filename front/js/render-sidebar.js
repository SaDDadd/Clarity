function renderProjectsSidebar() {
    elements.projectsList.innerHTML = "";

    getAccessibleProjects().forEach(project => {
        const admin = isProjectAdmin(project);
        const item = document.createElement("a");
        item.href = `#project-${project.id}`;
        item.className = "project";
        if (currentPage === "overview" && Number(project.id) === Number(currentProjectId)) {
            item.classList.add("active-project");
        }

        item.innerHTML = `
            <span class="project-dot purple"></span>
            <span class="project-name">${escapeHTML(project.name)}</span>
            <span class="project-role-badge ${admin ? "" : "member"}">${admin ? "A" : "У"}</span>
            ${admin ? `
                <span class="project-actions">
                    <button class="project-edit" type="button" aria-label="Редактировать проект">✎</button>
                    <button class="project-delete" type="button" aria-label="Удалить проект">×</button>
                </span>
            ` : ""}
        `;

        item.addEventListener("click", event => {
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