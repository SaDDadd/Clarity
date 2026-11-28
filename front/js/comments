// Комментарии: все участники проекта могут читать и создавать, автор/админ/куратор — изменять и удалять.
const commentsSection = document.getElementById("taskCommentsSection");
const commentsList = document.getElementById("taskCommentsList");
const commentsForm = document.getElementById("taskCommentForm");
const commentInput = document.getElementById("taskCommentText");
const commentSubmit = document.getElementById("taskCommentSubmit");
let commentsVersion = 0;
let commentTask = null;
let taskComments = [];
function closeTaskComments() {
    commentsVersion++;
    commentTask = null; taskComments = [];
    commentsList.replaceChildren(); commentsForm.reset(); commentsSection.classList.add("hidden");
}
function commentPath(task) { return `/projects/${task.projectId}/tasks/${task.id}/comments`; }
function isCommentView(task, generation, version) {
    return generation === sessionGeneration && version === commentsVersion && commentTask?.id === task.id && getProject(task.projectId);
}
function validateComment(text) {
    const value = String(text || "").trim();
    if (!value || value.length > 1000) throw new Error("Комментарий должен содержать от 1 до 1000 символов");
    return value;
}
function canManageComment(task, comment) {
    return Boolean(currentUser?.id != null && getProject(task.projectId) && (canManageProject(getProject(task.projectId)) || (comment.author_id != null && Number(comment.author_id) === Number(currentUser.id))));
}
function renderTaskComments() {
    const task = commentTask;
    if (!task) return;
    commentsList.replaceChildren();
    if (!taskComments.length) {
        const empty = document.createElement("p"); empty.textContent = "Комментариев пока нет."; commentsList.appendChild(empty);
    }
    taskComments.forEach(comment => {
        const row = document.createElement("article"); row.className = "task-comment";
        const meta = document.createElement("small");
        const author = document.createElement("strong"); author.textContent = comment.author_id == null ? "Удалённый пользователь" : `@${getNicknameById(comment.author_id)}`;
        meta.append(author, document.createTextNode(comment.created_date ? ` · ${new Date(comment.created_date).toLocaleString("ru-RU")}` : ""));
        const text = document.createElement("p"); text.textContent = comment.comment_text || "";
        row.append(meta, text);
        if (comment.author_id != null) ensureUserCached(comment.author_id).then(name => { if (name && author.isConnected) author.textContent = `@${name}`; });
        if (canManageComment(task, comment)) {
            const actions = document.createElement("div"); actions.className = "comment-actions";
            const editButton = document.createElement("button"); editButton.type = "button"; editButton.className = "small-action"; editButton.textContent = "Редактировать";
            const deleteButton = document.createElement("button"); deleteButton.type = "button"; deleteButton.className = "small-action danger"; deleteButton.textContent = "Удалить";
            editButton.addEventListener("click", () => {
                const editor = document.createElement("textarea"); editor.maxLength = 1000; editor.value = comment.comment_text; editor.setAttribute("aria-label", "Текст комментария");
                const save = document.createElement("button"); save.type = "button"; save.className = "small-action"; save.textContent = "Сохранить";
                const cancel = document.createElement("button"); cancel.type = "button"; cancel.className = "small-action"; cancel.textContent = "Отмена";
                row.replaceChildren(meta, editor, save, cancel); editor.focus();
                cancel.addEventListener("click", renderTaskComments);
                save.addEventListener("click", () => runButtonAction(save, async () => {
                    const value = validateComment(editor.value);
                    return withWriteLock(`comment:${comment.comment_id}`, async generation => {
                        if (!canManageComment(task, comment)) return false;
                        const version = commentsVersion;
                        await api("PUT", `${commentPath(task)}/${comment.comment_id}`, {comment_text:value});
                        assertSession(generation);
                        if (isCommentView(task, generation, version)) { comment.comment_text = value; renderTaskComments(); }
                        showToast("✓ Комментарий обновлён"); return true;
                    });
                }));
            });
            deleteButton.addEventListener("click", () => runButtonAction(deleteButton, () => withWriteLock(`comment:${comment.comment_id}`, async generation => {
                if (!canManageComment(task, comment) || !confirm("Удалить комментарий?")) return false;
                const version = commentsVersion;
                await api("DELETE", `${commentPath(task)}/${comment.comment_id}`);
                assertSession(generation);
                if (isCommentView(task, generation, version)) { taskComments = taskComments.filter(item => item.comment_id !== comment.comment_id); renderTaskComments(); }
                showToast("✓ Комментарий удалён"); return true;
            })));
            actions.append(editButton, deleteButton); row.appendChild(actions);
        }
        commentsList.appendChild(row);
    });
}
async function openTaskComments(task) {
    const generation = sessionGeneration, version = ++commentsVersion;
    commentTask = task; taskComments = [];
    commentsSection.classList.remove("hidden"); commentsForm.reset(); commentSubmit.disabled = true;
    commentsList.textContent = "Загрузка комментариев…";
    try {
        const items = await apiAll(commentPath(task));
        if (!isCommentView(task, generation, version)) return;
        taskComments = items; renderTaskComments();
    } catch (error) {
        if (isCommentView(task, generation, version)) {
            commentsList.textContent = getErrorMessage(error) + " ";
            const retry = document.createElement("button"); retry.type = "button"; retry.className = "small-action"; retry.textContent = "Повторить загрузку";
            retry.addEventListener("click", () => openTaskComments(task)); commentsList.appendChild(retry);
        }
    } finally { if (isCommentView(task, generation, version)) commentSubmit.disabled = false; }
}
commentsForm.addEventListener("submit", event => {
    event.preventDefault();
    const task = commentTask;
    if (!task || !getProject(task.projectId)) return;
    runButtonAction(commentSubmit, () => withWriteLock(`comment:create:${task.id}`, async generation => {
        const version = commentsVersion, value = validateComment(commentInput.value);
        const result = await api("POST", commentPath(task), {comment_text:value});
        assertSession(generation);
        if (isCommentView(task, generation, version)) {
            commentsForm.reset();
            if (result?.comment_id != null) { taskComments.push(result); renderTaskComments(); }
            else await openTaskComments(task);
        }
        showToast("✓ Комментарий добавлен"); return true;
    }));
});
