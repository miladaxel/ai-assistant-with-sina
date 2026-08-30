// js/class-detail.js

import { classDetailData, studentReports } from './store.js';

class ClassDetailManager {
    constructor() {
        this.data = classDetailData;
        this.reports = studentReports; // داده‌های کارنامه
        this.init();
    }

    init() {
        this.renderBreadcrumb();
        this.renderStudents(); // لیست دانش‌آموزان
        this.renderExams();    // لیست آزمون‌ها
        this.attachTabEvents();
    }

    renderBreadcrumb() {
        const container = document.getElementById('breadcrumb-area');
        if (!container) return;
        
        let html = '';
        this.data.info.breadcrumb.forEach((item, index) => {
            if (index > 0) html += `<span class="breadcrumb-separator">/</span>`;
            if (item.active) {
                html += `<span class="active">${item.text}</span>`;
            } else {
                html += `<a href="${item.href}">${item.text}</a>`;
            }
        });
        container.innerHTML = html;
    }

    // --- 1. رندر لیست دانش‌آموزان با دکمه‌های فعال ---
    renderStudents() {
        const container = document.getElementById('students-list');
        if (!container) return;

        container.innerHTML = this.data.students.filter(u=>u.class==localStorage.getItem("class")).map((st,index) => `
           <div class="student-row">
    <div class="st-info">
        <div class="st-index">
            ${index+1}
        </div>

        <img src="${st.avatar}" class="st-avatar" alt="${st.name}">
        
        <div class="st-text-details">
            <span class="st-name">${st.name}</span>
            <span class="st-class-name">${st.class || ''}</span> </div>
    </div>

    <div class="btn-group">
        <button class="btn-sm btn-outline-indigo" onclick="alert('تمرین برای ${st.name}')">
            تمرین‌ها
        </button>
        <button class="btn-sm btn-outline-blue" onclick="window.openReport('${st.id}')">
            آزمون‌ها
        </button>
        <button class="btn-sm btn-outline-indigo" onclick="alert('تحلیل ${st.name}')">
            تحلیل
        </button>
    </div>
</div>
        `).join('');
    }

    // --- 2. رندر لیست آزمون‌ها ---
    renderExams() {
        const container = document.getElementById('exams-grid');
        if (!container) return;

        container.innerHTML = this.data.exams.filter(u=>u.class==localStorage.getItem("class")).map(ex => {
            let badgeClass = 'badge-closed';
            if (ex.status === 'closed') badgeClass = 'badge-active';
            if (ex.status === 'pending') badgeClass = 'badge-draft';

            // لینک به صفحه ماتریس نمرات (exam-entry.html)
            return `
            <a href="exam-entry.html?exam_id=${ex.id}" class="exam-card">
            <span class="exam-title">${ex.title}</span>
            <span class="exam-date"><i class="fa-regular fa-calendar"></i> ${ex.date}</span>
            <span class="badge ${badgeClass}">${ex.status_label}</span>
            </a>
            `;
        }).join('');
    }

    // --- 3. لاجیک باز کردن مودال کارنامه (Logic اصلی جدید) ---
    openReport(studentId) {
        const report = this.reports[studentId];
        
        // اگر کارنامه‌ای برای این دانش‌آموز در store نباشد
        if (!report) {
            alert("داده‌های آزمون برای این دانش‌آموز یافت نشد (دیتای تستی برای st_1 و st_2 موجود است).");
            return;
        }

        // تنظیم تیتر مودال
        document.getElementById('modal-title').innerText = `${report.student_name} - ${report.exam_title}`;

        // ساخت لیست سوالات با وضعیت رنگی
        let questionsHtml = report.questions.map((q, index) => {
            let icon = '', statusClass = '';
            
            // تعیین استایل بر اساس وضعیت
            switch (q.status) {
                case 'correct':
                    icon = 'fa-check';
                    statusClass = 'status-correct'; // سبز
                    break;
                case 'wrong':
                    icon = 'fa-xmark';
                    statusClass = 'status-wrong'; // قرمز
                    break;
                case 'partial':
                    icon = 'fa-minus';
                    statusClass = 'status-partial'; // زرد
                    break;
                default:
                    icon = 'fa-circle';
                    statusClass = '';
            }

            return `
                <li class="q-item ${statusClass}">
                    <div class="q-topic">
                        <span style="opacity:0.5; font-size:0.8rem; width:25px;">س ${index + 1}</span>
                        ${q.topic}
                    </div>
                    <div class="q-score">
                        ${q.score} <i class="fa-solid ${icon}" style="margin-right:5px; width:15px; text-align:center;"></i>
                    </div>
                </li>
            `;
        }).join('');

        // پر کردن بدنه مودال
        const modalBody = document.getElementById('modal-body');
        modalBody.innerHTML = `
            <div class="score-circle">
                <span class="score-value">${report.total_score}</span>
                <span class="score-label">از ${report.max_score}</span>
            </div>
            
            <div style="margin-bottom:10px; font-weight:bold; color:#64748b; font-size:0.9rem;">ریز عملکرد سوالات:</div>
            
            <ul class="question-list">
                ${questionsHtml}
            </ul>

            <button class="btn-sm btn-outline-blue" style="width:100%; margin-top:20px; padding:12px; text-align:center;" onclick="document.getElementById('report-modal').classList.remove('open')">
                بستن کارنامه
            </button>
        `;

        // نمایش مودال (اضافه کردن کلاس open)
        document.getElementById('report-modal').classList.add('open');
    }

    // --- 4. مدیریت تب‌ها ---
    attachTabEvents() {
        const tabs = document.querySelectorAll('.tab-btn');
        const contents = document.querySelectorAll('.tab-content');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                contents.forEach(c => c.classList.remove('active'));

                tab.classList.add('active');
                const targetId = tab.dataset.target;
                const targetContent = document.getElementById(targetId);
                if(targetContent) targetContent.classList.add('active');
            });
        });
    }
}

// مقداردهی اولیه و اتصال به Window
document.addEventListener('DOMContentLoaded', () => {
    const manager = new ClassDetailManager();
    
    // اکسپوز کردن تابع به Window تا از داخل HTML قابل صدا زدن باشد
    window.openReport = (id) => manager.openReport(id);
});