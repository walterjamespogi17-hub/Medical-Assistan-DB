// Dark mode toggle
document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.getElementById('dark-mode-toggle');
    if (toggleButton) {
        toggleButton.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDark);
            toggleButton.textContent = isDark ? 'Light Mode' : 'Dark Mode';
        });

        // Load saved preference
        const savedDarkMode = localStorage.getItem('darkMode');
        if (savedDarkMode === 'true') {
            document.body.classList.add('dark-mode');
            toggleButton.textContent = 'Light Mode';
        } else {
            toggleButton.textContent = 'Dark Mode';
        }
    }
});