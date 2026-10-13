function applyTheme() {
    let dark = settings.theme === "dark";
    if (settings.theme === "system") {
        dark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    }
    document.body.classList.toggle("theme-dark", dark);
}