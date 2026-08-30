// js/exams.js

document.addEventListener('DOMContentLoaded', () => {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const btnAI = document.getElementById('btnAI');
    const btnAiText = document.getElementById('btnAiText');
    const uploadText = document.getElementById('uploadText');
    const fileNameDisplay = document.getElementById('fileName');

    // 1. کلیک روی ناحیه آپلود
    uploadZone.addEventListener('click', () => {
        fileInput.click();
    });

    // 2. هندل کردن تغییر فایل (وقتی فایلی انتخاب شد)
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            
            // تغییر استایل آپلود زون
            uploadZone.classList.add('filled');
            uploadText.innerText = 'فایل انتخاب شد';
            fileNameDisplay.innerText = file.name;
            uploadZone.querySelector('i').className = 'fa-solid fa-file-circle-check fa-3x';

            // فعال کردن دکمه هوش مصنوعی
            btnAI.classList.remove('inactive');
            btnAI.classList.add('active');
            btnAI.disabled = false;
            btnAiText.innerText = 'تحلیل توسط هوش مصنوعی ✨';
        }
    });

    // 3. کلیک روی دکمه هوش مصنوعی
    btnAI.addEventListener('click', () => {
        btnAiText.innerText = 'در حال تحلیل...';
        setTimeout(() => {
            alert('تحلیل هوش مصنوعی کامل شد! (شبیه‌سازی)');
            btnAiText.innerText = 'تحلیل مجدد';
        }, 2000);
    });
});

// 4. تابع تاگل کردن تگ‌ها (خارج از DOMContentLoaded برای دسترسی از HTML)
function toggleTag(element) {
    element.classList.toggle('selected');
}