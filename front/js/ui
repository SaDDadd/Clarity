// Управление мобильной навигацией, фокусом диалогов и действиями с кнопок.
const mobileMenuButton = document.getElementById("mobileMenuButton");
const mobileSidebar = document.getElementById("mobileSidebar");
const modalOpeners = new Map();
function closeMobileMenu() {
    mobileSidebar.classList.remove("mobile-open");
    mobileMenuButton.setAttribute("aria-expanded", "false");
}
function toggleMobileMenu() {
    const opened = mobileSidebar.classList.toggle("mobile-open");
    mobileMenuButton.setAttribute("aria-expanded", String(opened));
    if (opened) mobileSidebar.querySelector("a")?.focus();
}
mobileMenuButton.addEventListener("click", toggleMobileMenu);
mobileSidebar.addEventListener("click", event => {
    if (event.target.closest("a, button")) closeMobileMenu();
});
document.addEventListener("click", event => {
    if (!mobileSidebar.contains(event.target) && !mobileMenuButton.contains(event.target)) closeMobileMenu();
});
window.matchMedia("(max-width: 700px)").addEventListener?.("change", closeMobileMenu);

function dialogControls(modal) {
    return [...modal.querySelectorAll('button:not(:disabled), input:not(:disabled), textarea:not(:disabled), select:not(:disabled), a[href], [tabindex]:not([tabindex="-1"])')]
        .filter(element => element.getClientRects().length > 0);
}
function showDialog(modal, initialFocus) {
    const opener = document.activeElement;
    modalOpeners.set(modal, opener);
    modal.classList.remove("hidden");
    elements.app.inert = true;
    const controls = dialogControls(modal);
    const initial = initialFocus && controls.includes(initialFocus) ? initialFocus : controls[0];
    initial?.focus();
}
function hideDialog(modal) {
    if (modal.classList.contains("hidden")) return;
    modal.classList.add("hidden");
    if (!activeDialog()) elements.app.inert = false;
    const opener = modalOpeners.get(modal);
    modalOpeners.delete(modal);
    if (opener?.isConnected && opener.getClientRects().length) opener.focus();
    else if (!elements.app.classList.contains("hidden")) (mobileMenuButton.getClientRects().length ? mobileMenuButton : elements.searchInput).focus();
}
function activeDialog() {
    return [elements.taskModal, elements.projectModal, elements.membersModal].find(modal => !modal.classList.contains("hidden"));
}
document.addEventListener("keydown", event => {
    const modal = activeDialog();
    if (event.key === "Tab" && modal) {
        const controls = dialogControls(modal), first = controls[0], last = controls.at(-1);
        if (!first) { event.preventDefault(); return; }
        if (!modal.contains(document.activeElement) || (event.shiftKey && document.activeElement === first) || (!event.shiftKey && document.activeElement === last)) {
            event.preventDefault(); (event.shiftKey ? last : first).focus();
        }
    }
    if (event.key === "Escape" && !modal && mobileSidebar.classList.contains("mobile-open")) {
        closeMobileMenu(); mobileMenuButton.focus();
    }
});
function bindTaskKeyboard(element, taskId) {
    element.tabIndex = 0;
    element.setAttribute("aria-label", "Открыть задачу");
    element.addEventListener("keydown", event => {
        if (event.target !== element || !["Enter", " "].includes(event.key)) return;
        event.preventDefault(); openTaskModal("todo", taskId);
    });
}
async function runButtonAction(button, action) {
    if (button.disabled) return false;
    button.disabled = true;
    try { return await action(); }
    catch (error) { showToast(getErrorMessage(error)); return false; }
    finally { button.disabled = false; }
}

let taskFormVersion = 0;
let projectFormVersion = 0;
