// js/settings.js

// باز کردن مودال
function openSchoolModal() {
    const modal = document.getElementById('schoolModal');
    modal.classList.add('open');
}

// بستن مودال
function closeSchoolModal() {
    const modal = document.getElementById('schoolModal');
    modal.classList.remove('open');
}

// بستن با کلیک بیرون از باکس
document.getElementById('schoolModal').addEventListener('click', (e) => {
    if (e.target.id === 'schoolModal') closeSchoolModal();
});

// تغییر مدرسه
function changeSchool(schoolId) {
    console.log(`Switching to school: ${schoolId}`);
    
    // ذخیره در دیتابیس لوکال
    localStorage.setItem('selected_school', schoolId);
    
    // شبیه‌سازی لودینگ و رفرش داشبورد
    // چون MPA هستیم، به داشبورد هدایت می‌کنیم تا با کانتکست جدید لود شود
    document.body.style.cursor = 'wait';
    setTimeout(() => {
        window.location.href = 'dashboard.html';
    }, 500);
}