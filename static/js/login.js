// js/login.js

// 1. هندل کردن سابمیت فرم ورود
function handleLogin(event) {
    event.preventDefault(); // جلوگیری از رفرش صفحه

    const nationalId = document.getElementById('national_id').value;
    const personnelId = document.getElementById('personnel_id').value;
    const password = document.getElementById('password').value;

    // شبیه‌سازی اعتبارسنجی ساده
    if(nationalId && personnelId && password) {
        // اگر اطلاعات پر بود، مودال مدرسه را باز کن
        openSchoolModal();
    } else {
        alert("لطفاً تمام فیلدها را پر کنید.");
    }
}

// 2. باز کردن مودال انتخاب مدرسه
function openSchoolModal() {
    const modal = document.getElementById('schoolModal');
    modal.classList.add('open');
}

// 3. انتخاب مدرسه و ورود نهایی
function selectSchool(schoolId) {
    console.log(`School selected: ${schoolId}`);
    
    // ذخیره کردن مدرسه در لوکال استوریج (اختیاری)
    localStorage.setItem('selected_school', schoolId);
    
    // هدایت به داشبورد
    // کمی تاخیر برای دیدن افکت کلیک
    setTimeout(() => {
        window.location.href = 'dashboard.html';
    }, 300);
}