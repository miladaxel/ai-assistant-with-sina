
    const menuBtn = document.getElementById('mobile-menu-btn');
    const navMenu = document.getElementById('nav-menu');
    const overlay = document.getElementById('nav-overlay');

    // تابع باز/بسته کردن
    function toggleMenu() {
        navMenu.classList.toggle('active');
        overlay.classList.toggle('active');
        
        // تغییر آیکون همبرگری به ضربدر
        const icon = menuBtn.querySelector('i');
        if (navMenu.classList.contains('active')) {
            icon.classList.remove('fa-bars');
            icon.classList.add('fa-xmark');
        } else {
            icon.classList.remove('fa-xmark');
            icon.classList.add('fa-bars');
        }
    }

    menuBtn.addEventListener('click', toggleMenu);
    overlay.addEventListener('click', toggleMenu); // بستن با کلیک روی فضای خالی
