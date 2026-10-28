function setAuthMessage(message = "", success = false) {
    elements.authMessage.textContent = message;
    elements.authMessage.classList.toggle("success", success);
}

function setAuthMode(mode) {
    authMode = mode === "register" ? "register" : "login";
    const registering = authMode === "register";

    elements.loginTab.classList.toggle("active", !registering);
    elements.registerTab.classList.toggle("active", registering);
    elements.authNameField.classList.toggle("hidden", !registering);
    elements.authConfirmField.classList.toggle("hidden", !registering);
    elements.authNameInput.required = registering;
    elements.authConfirmInput.required = registering;
    elements.authPasswordInput.autocomplete = registering ? "new-password" : "current-password";
    elements.authLoginLabel.textContent = registering ? "E-mail" : "Ник или e-mail";
    elements.authEmailInput.type = registering ? "email" : "text";
    elements.authEmailInput.autocomplete = registering ? "email" : "username";
    elements.authEmailInput.placeholder = registering ? "name@example.com" : "@nickname или name@example.com";
    elements.authSubmitButton.textContent = registering ? "Создать аккаунт" : "Войти";
    setAuthMessage();
}

function showAuthScreen(mode = "login") {
    elements.app.classList.add("hidden");
    elements.authScreen.classList.remove("hidden");
    elements.authForm.reset();
    setAuthMode(mode);
    setTimeout(() => elements.authEmailInput.focus(), 30);
}

async function enterAccount(profile) {
    mapProfileFromServer(profile);
    settings = loadSettings();

    const savedPage = localStorage.getItem(userStorageKey(STORAGE.currentPage));
    const savedView = localStorage.getItem(userStorageKey(STORAGE.currentView));
    const savedProject = localStorage.getItem(userStorageKey(STORAGE.currentProject));

    currentPage = ["overview", "my-tasks", "favorites", "projects", "settings", "invitations"].includes(savedPage)
        ? savedPage : "overview";
    currentView = ["board", "list", "calendar"].includes(savedView) ? savedView : "board";
    currentProjectId = savedProject ? Number(savedProject) : null;

    await loadWorkspaceFromServer();
    await loadInvitations();

    if (!getAccessibleProjects().some(project => Number(project.id) === Number(currentProjectId))) {
        currentProjectId = getAccessibleProjects()[0]?.id || null;
    }

    elements.authScreen.classList.add("hidden");
    elements.app.classList.remove("hidden");
    elements.searchInput.value = "";
    resetFilters(false);
    applyTheme();
    saveSettings();
    render();

    if (currentPage === "overview" && currentProjectId) {
        try { await loadProjectDetails(currentProjectId); } catch (error) { showToast(getErrorMessage(error)); }
    }
}

async function registerAccount() {
    const nickname = cleanNickname(elements.authNameInput.value);
    const email = elements.authEmailInput.value.trim();
    const password = elements.authPasswordInput.value;
    const confirmPassword = elements.authConfirmInput.value;

    if (!nickname) throw new Error("Введите ник.");
    validateNickname(nickname);
    if (!email) throw new Error("Введите e-mail.");
    if (password.length < 6) throw new Error("Пароль должен содержать минимум 6 символов.");
    if (password !== confirmPassword) throw new Error("Пароли не совпадают.");

    await api("POST", "/auth/register", {
        username: nickname,
        email,
        password
    });

    const login = await api("POST", "/auth/login", {
        username_or_email: nickname,
        password
    });

    if (!login?.access_token) throw new Error("Сервер не вернул токен.");
    setToken(login.access_token);

    const profile = await api("GET", "/profile");
    await enterAccount(profile);
    showToast("✓ Аккаунт создан");
}

async function signInAccount() {
    const identifier = elements.authEmailInput.value.trim();
    const password = elements.authPasswordInput.value;
    if (!identifier) throw new Error("Введите ник или e-mail.");

    const result = await api("POST", "/auth/login", {
        username_or_email: identifier,
        password
    });

    if (!result?.access_token) throw new Error("Сервер не вернул токен.");
    setToken(result.access_token);

    const profile = await api("GET", "/profile");
    await enterAccount(profile);
}

function signOutAccount() {
    clearToken();
    clearLocalWorkspace();
    settings = { ...DEFAULT_SETTINGS };
    user = { ...DEFAULT_USER };
    closeTaskModal();
    closeProjectModal();
    closeAllFloatingMenus();
    showAuthScreen("login");
}

async function initializeAuth() {
    const token = getToken();
    if (!token) {
        showAuthScreen("login");
        return;
    }

    try {
        const profile = await api("GET", "/profile");
        await enterAccount(profile);
    } catch (error) {
        clearToken();
        clearLocalWorkspace();
        showAuthScreen("login");
    }
}