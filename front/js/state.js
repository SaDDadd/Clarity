// Файл с глобальным состоянием приложения

let currentUser = null; // Данные текущего авторизованного пользователя
let authMode = "login"; // Текущий режим экрана авторизации
let projects = []; // Массив всех доступных проектов
let tasks = []; // Массив всех доступных задач
let settings = { ...DEFAULT_SETTINGS }; // Настройки интерфейса (тема, сортировка)
let user = { ...DEFAULT_USER }; // Данные пользователя для UI
let currentProjectId = null; // ID выбранного проекта
let currentPage = "overview"; // Текущая страница (overview, my-tasks и т.д.)
let currentView = "board"; // Текущий вид (board, list, calendar)
let currentTaskMenuId = null; // ID задачи, для которой открыто контекстное меню
let draggedTaskId = null; // ID задачи, которая перетаскивается в данный момент
let calendarCursor = new Date(); // Текущая дата для навигации по календарю
let currentProjectDetails = null; // Детали текущего проекта
let invitations = []; // Массив входящих приглашений
let projectTaskCache = new Map(); // Кэш задач по ID проекта
const userCache = new Map(); // Кэш никнеймов пользователей по ID

// Текущие активные фильтры
const filters = {
    status: "all",
    priority: "all",
    project: "all",
    overdue: false
};