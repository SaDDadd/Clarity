let currentUser = null;
let authMode = "login";
let projects = [];
let tasks = [];
let settings = { ...DEFAULT_SETTINGS };
let user = { ...DEFAULT_USER };
let currentProjectId = null;
let currentPage = "overview";
let currentView = "board";
let currentTaskMenuId = null;
let draggedTaskId = null;
let calendarCursor = new Date();
let currentProjectDetails = null;
let invitations = [];
let projectTaskCache = new Map();
const userCache = new Map();

const filters = {
    status: "all",
    priority: "all",
    project: "all",
    overdue: false
};