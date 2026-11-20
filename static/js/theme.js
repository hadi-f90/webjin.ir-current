(function () {
    const root = document.documentElement;
    let theme = 'light';

    try {
        theme = localStorage.getItem('theme') === 'dark' ? 'dark' : 'light';
    } catch (error) {
        console.warn('Unable to read the saved theme preference.', error);
    }

    root.setAttribute('data-theme', theme);

    function updateThemeIcon(icon, currentTheme) {
        icon.classList.toggle('bi-sun-fill', currentTheme === 'dark');
        icon.classList.toggle('bi-moon-fill', currentTheme !== 'dark');
    }

    document.addEventListener('DOMContentLoaded', function () {
        const toggle = document.getElementById('themeToggle');
        const icon = document.getElementById('themeIcon');
        if (!toggle || !icon) return;

        updateThemeIcon(icon, theme);
        toggle.addEventListener('click', function () {
            theme = theme === 'dark' ? 'light' : 'dark';
            root.setAttribute('data-theme', theme);
            updateThemeIcon(icon, theme);

            try {
                localStorage.setItem('theme', theme);
            } catch (error) {
                console.warn('Unable to save the theme preference.', error);
            }
        });
    });
})();
