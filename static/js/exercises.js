// js/exercises.js
import { exerciseStudentsData } from './store.js';

class ExerciseManager {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.data = exerciseStudentsData;
        this.sortSelect = document.getElementById('sortSelect');
        this.init();
    }

    init() {
        this.renderList('ai_priority'); // پیش‌فرض

        // لیسنر تغییر مرتب‌سازی
        this.sortSelect.addEventListener('change', (e) => {
            this.renderList(e.target.value);
        });
    }

    renderList(sortType) {
        this.container.innerHTML = '';
        let sortedData = [...this.data];

        if (sortType === 'ai_priority') {
            // کسانی که نیاز به تمرین دارند اول بیایند
            sortedData.sort((a, b) => (a.needs_exercise === b.needs_exercise) ? 0 : a.needs_exercise ? -1 : 1);
        } else if (sortType === 'alphabetical') {
            sortedData.sort((a, b) => a.name.localeCompare(b.name));
        }

        sortedData.forEach(st => {
            // ساخت دکمه هوشمند
            let actionBtn = '';
            let reasonHtml = '';

            if (st.needs_exercise) {
                // اگر نیاز به تمرین دارد
                reasonHtml = `<div class="st-reason"><i class="fa-solid fa-triangle-exclamation"></i> ${st.reason}</div>`;
                actionBtn = `
                    <button class="btn-action btn-primary-action" onclick="openGeneratorModal()">
                        <span class="fas fa-plus"></span> ایجاد تمرین
                    </button>
                `;
            } else {
                // وضعیت عادی
                reasonHtml = `<div style="font-size:0.75rem; color:#94a3b8">وضعیت پایدار</div>`;
                actionBtn = `
                    <button class="btn-action btn-secondary-action " onclick="alert('مشاهده تاریخچه ${st.name}')">
                        <span class="fas fa-book"></span>تاریخچه
                    </button>
                `;
            }

            const row = document.createElement('div');
            row.className = 'student-row';
            row.innerHTML = `
                <div class="st-left">
                    <img src="${st.avatar}" class="st-avatar">
                    <div>
                        <span class="st-name">${st.name}</span>
                        ${reasonHtml}
                    </div>
                </div>
                <div>${actionBtn}</div>
            `;
            this.container.appendChild(row);
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ExerciseManager('studentsList');
});