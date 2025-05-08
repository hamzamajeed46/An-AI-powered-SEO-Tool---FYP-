const toggleButton = document.getElementById('theme-toggle');
const body = document.body;

const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
    body.className = savedTheme;
    toggleButton.textContent = savedTheme === 'dark-theme' ? '☀️' : '🌙';
}

toggleButton.addEventListener('click', () => {
    body.classList.toggle('dark-theme');
    body.classList.toggle('light-theme');

    const newTheme = body.classList.contains('dark-theme') ? 'dark-theme' : 'light-theme';
    toggleButton.textContent = newTheme === 'dark-theme' ? '☀️' : '🌙';
    localStorage.setItem('theme', newTheme);
});
