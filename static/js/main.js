document.addEventListener('DOMContentLoaded', () => {
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('nav-menu');

    hamburger.addEventListener('click', () => {
        // Додаємо або забираємо клас 'active' при кліку
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });

    // Опціонально: закривати меню при кліку на посилання
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });
});