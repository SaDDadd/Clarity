function mapProfileFromServer(profile) {
    const nickname = cleanNickname(profile?.username || "Пользователь");
    const mapped = {
        id: Number(profile?.user_id),
        username: nickname,
        nickname,
        name: nickname,
        email: String(profile?.email || ""),
        createdAt: profile?.created_date || null
    };
    currentUser = mapped;
    user = { ...DEFAULT_USER, ...mapped };
    userCache.set(mapped.id, nickname);
    return mapped;
}

function mapTaskFromServer(task) {
    const rawStatus = String(task?.task_status || task?.status || "pending");
    return {
        id: Number(task?.task_id ?? task?.id),
        projectId: Number(task?.project_id ?? task?.projectId),
        assigneeId: task?.assigned_to == null ? null : Number(task.assigned_to),
        title: String(task?.title || "Без названия"),
        description: String(task?.task_description ?? task?.description ?? ""),
        priority: ["high", "medium", "low"].includes(task?.task_priority) ? task.task_priority : "medium",
        date: task?.deadline ? String(task.deadline).slice(0, 10) : "",
        status: statusFromBackend[rawStatus] || "todo",
        favorite: Boolean(task?.task_favorite),
        createdAt: task?.created_date || null,
        updatedAt: task?.updated_date || task?.created_date || null
    };
}

function mapTaskToServer(payload) {
    const result = {
        title: String(payload.title || "").trim(),
        task_description: String(payload.description || "").trim(),
        task_status: statusToBackend[payload.status] || payload.status || "pending",
        task_priority: ["low", "medium", "high"].includes(payload.priority) ? payload.priority : "medium",
        task_favorite: Boolean(payload.favorite),
        assigned_to: payload.assigneeId === "" || payload.assigneeId == null ? null : Number(payload.assigneeId),
        deadline: payload.date ? String(payload.date).slice(0, 10) : null
    };
    return result;
}

function mapProjectFromServer(project) {
    const adminId = Number(project?.admin_id ?? project?.adminId);
    const members = Array.isArray(project?.members) ? project.members : [];
    const memberIds = members
        .map(member => Number(member?.user_id ?? member?.id))
        .filter(id => Number.isInteger(id) && id !== adminId);

    return {
        id: Number(project?.project_id ?? project?.id),
        adminId,
        ownerId: adminId,
        name: String(project?.project_name ?? project?.name ?? "Без названия"),
        description: String(project?.project_description ?? project?.description ?? ""),
        memberIds: [...new Set(memberIds)],
        role: project?.role || (adminId === currentUser?.id ? "admin" : "member"),
        createdAt: project?.created_date || null,
        members
    };
}

function getInvitationId(invitation) {
    return Number(invitation?.invitation_id ?? invitation?.id);
}

function mapInvitation(invitation) {
    return {
        id: getInvitationId(invitation),
        projectId: Number(invitation?.project_id ?? invitation?.project?.project_id),
        projectName: String(invitation?.project_name ?? invitation?.project?.project_name ?? "Проект"),
        inviterId: invitation?.inviter_id == null ? null : Number(invitation.inviter_id),
        message: String(invitation?.message || ""),
        createdAt: invitation?.created_date || invitation?.createdAt || null,
        raw: invitation
    };
}