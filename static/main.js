document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;

    // Check for saved theme preference, default to light theme
    const savedTheme = localStorage.getItem('theme') || 'light-theme';
    body.classList.add(savedTheme);

    // Update theme toggle button text based on current theme
    const updateThemeToggleText = () => {
        themeToggle.textContent = body.classList.contains('dark-theme') ? '☀️' : '🌙';
    };

    // Initial theme toggle text
    updateThemeToggleText();

    themeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-theme');
        const currentTheme = body.classList.contains('dark-theme') ? 'dark-theme' : 'light-theme';
        localStorage.setItem('theme', currentTheme);
        updateThemeToggleText();
    });
});
