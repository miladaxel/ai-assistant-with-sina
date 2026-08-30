// js/layout.js

function createSidebar() {
  const sidebar = document.createElement("div");
  sidebar.className = "sidebar";

  // تشخیص اینکه الان در کدام صفحه هستیم برای اکتیو کردن منو
  const path = window.location.pathname;

  sidebar.innerHTML = `
        <a href="${SITE_URLS.home}">
            <div style="display:flex;align-items: center;column-gap: 10px;margin-bottom:1rem;justify-content:center">
                <img style="width:230px;" src="${SIDEBAR_ICONS.logo}" />
            </div>
        </a>
        <nav>
            <a href="${SITE_URLS.profile}" class="nav-item ${path.includes(SITE_URLS.profile) ? 'active' : ''}">
                <img class="icon-template" src="${SIDEBAR_ICONS.profile}" />
                پروفایل شخصی
            </a>
            <a href="${SITE_URLS.classes}" class="nav-item ${path.includes(SITE_URLS.classes) ? 'active' : ''}"> 
                <img class="icon-template" src="${SIDEBAR_ICONS.classes}" />
                مدیریت کلاس‌ ها
            </a>  
            <a href="${SITE_URLS.exams}" class="nav-item ${path.includes(SITE_URLS.exams) ? 'active' : ''}">
                <img class="icon-template" src="${SIDEBAR_ICONS.exams}" /> 
                مدیریت آزمون ها
            </a>  
            <a href="${SITE_URLS.analysis}" class="nav-item ${path.includes(SITE_URLS.analysis) ? 'active' : ''}">
                <img class="icon-template" src="${SIDEBAR_ICONS.analysis}" />
                تحلیل‌ ها
            </a>
            <a href="${SITE_URLS.exercise}" class="nav-item ${path.includes(SITE_URLS.exercise) ? 'active' : ''}">
                <img class="icon-template" src="${SIDEBAR_ICONS.exercise}" />
                تمرین ها
            </a>
            <a href="${SITE_URLS.memo}" class="nav-item ${path.includes(SITE_URLS.memo) ? 'active' : ''}">
                <img class="icon-template" src="${SIDEBAR_ICONS.memo}" />
                یادداشت ها
            </a>
            <a href="${SITE_URLS.setting}" class="nav-item ${path.includes(SITE_URLS.setting) ? 'active' : ''}">
                <img class="icon-template" src="${SIDEBAR_ICONS.settings}" />
                تنظیمات
            </a>
            
            <a href="${SITE_URLS.home}" class="nav-item" style="justify-content: center; margin-top: 10px;">
                 بازگشت به خانه
            </a>
        </nav>
    `;

  // اضافه کردن به اول بادی
  document.body.prepend(sidebar);
}

// اجرا شدن تابع
createSidebar();

// اجرا شدن تابع به محض لود شدن فایل
createSidebar();




// // js/layout.js
//
// function createSidebar() {
//   const sidebar = document.createElement("div");
//   sidebar.className = "sidebar";
//
//   // تشخیص اینکه الان در کدام صفحه هستیم برای اکتیو کردن منو
//   const path = window.location.pathname;
//
//   sidebar.innerHTML = `
//         <a href="index.html">
//         <div style="display:flex;align-items: center;column-gap: 10px;margin-bottom:1rem ;justify-content:center" >
//         <img style="width:230px;" src="${SITE_URLS.img}" />
//         </div>
//         </a>
//         <nav>
//             <a href="${SITE_URLS.profile}" class="nav-item ${
//               path.includes("dashboard.html") ? "active" : ""
//             }">
//                 <span>🏠</span> پروفایل شخصی
//             </a>
//             <a href="${SITE_URLS.classes}" class="nav-item ${
//               path.includes("classes.html") ? "active" : ""
//             }">
//                 <span>👨‍🏫</span> مدیریت کلاس‌ ها
//             </a>
//               <a href="${SITE_URLS.exams}" class="nav-item ">
//                 <span>👨‍🎓</span> مدیریت آزمون ها
//             </a>
//             <a href="${SITE_URLS.analysis}" class="nav-item">
//                 <span>📊</span> تحلیل‌ ها
//             </a>
//             <a href="${SITE_URLS.exercise}" class="nav-item ${path.includes("settings.html") ? "active" : "" }">
//                 <span>📝</span> تمرین ها
//             </a>
//              <a href="${SITE_URLS.memo}" class="nav-item ${path.includes("settings.html") ? "active" : "" }">
//                 <span>🖇️</span> یادداشت ها
//               </a>
//             <a href="${SITE_URLS.setting}" class="nav-item ${path.includes("settings.html") ? "active" : "" }">
//                 <span>⚙️</span> تنظیمات
//             </a>
//             <a href="${SITE_URLS.home}" class="nav-item" style="justify-content: center;">
//                  بازگشت به خانه
//             </a>
//
//         </nav>
//     `;
//
//   // اضافه کردن به اول بادی
//   document.body.prepend(sidebar);
// }
//
// // اجرا شدن تابع به محض لود شدن فایل
// createSidebar();
