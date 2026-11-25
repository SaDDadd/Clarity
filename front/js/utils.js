// Файл с вспомогательными функциями (валидация, форматирование, безопасность)

// Очистка ника от лишних пробелов и символа @
function cleanNickname(value) {
    return String(value || "").trim().replace(/^@+/, "");
}

// Нормализация ника (приведение к нижнему регистру)
function normalizeNickname(value) {
    return cleanNickname(value).toLowerCase();
}

// Проверка валидности e-mail
function isValidEmail(value) {
    const text = String(value || "").trim();
    // Регулярное выражение проверяет наличие текста до @, самого @ и домена с точкой
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(text);
}

// Валидация ника (длина и допустимые символы)
function validateNickname(nickname) {
    if (nickname.length < 3 || nickname.length > 30) {
        throw new Error("Ник должен содержать от 3 до 30 символов.");
    }
    // Разрешены буквы (рус/англ), цифры, точка, дефис и подчёркивание
    if (!/^[A-Za-zА-Яа-яЁё0-9._-]+$/.test(nickname)) {
        throw new Error("В нике разрешены буквы, цифры, точка, дефис и подчёркивание.");
    }
}

// Безопасное экранирование HTML-тегов
function escapeHTML(value) {
    const div = document.createElement("div");
    div.textContent = value ?? "";
    return div.innerHTML;
}

// Безопасное экранирование значений для HTML-атрибутов
function escapeAttribute(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

// Форматирование даты из ISO в ДД.ММ.ГГГГ
function formatDate(date) {
    if (!date) return "Без срока";
    const parts = String(date).slice(0, 10).split("-");
    return parts.length === 3 ? `${parts[2]}.${parts[1]}.${parts[0]}` : date;
}

// Получение сегодняшней даты в формате ISO
function getTodayISO() {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
}

// Проверка, просрочена ли задача
function isOverdue(task) {
    return Boolean(task.date && task.date < getTodayISO() && task.status !== "done");
}

// Получение инициалов пользователя для аватара
function getInitials(name) {
    const text = String(name || "C").trim();
    if (!text) return "C";
    return text.split(/\s+/).slice(0, 2).map(part => part[0]?.toUpperCase() || "").join("") || "C";
}

// Показ всплывающего уведомления (тоста)
function showToast(message) {
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = message;
    elements.toastContainer.appendChild(toast);
    setTimeout(() => toast.remove(), 2600);
}

// Извлечение текста ошибки из объекта
function getErrorMessage(error) {
    return error?.message || "Не удалось выполнить операцию.";
}

// Сравнение дат для сортировки
function compareDates(a, b, direction) {
    if (!a && !b) return 0;
    if (!a) return 1;
    if (!b) return -1;
    return String(a).localeCompare(String(b)) * direction;
}

// Преобразование даты в локальный формат ISO (ГГГГ-ММ-ДД)
function toLocalISO(date) {
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}