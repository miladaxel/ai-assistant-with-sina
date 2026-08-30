// js/exam-matrix.js
import { examMatrixData } from './store.js';

class MatrixRenderer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.data = examMatrixData;
        this.init();
    }

    init() {
        this.renderHeaderInfo();
        this.renderTable();
    }

    renderHeaderInfo() {
        document.getElementById('exam-title').innerText = this.data.config.exam_title;
        document.getElementById('exam-date').innerText = this.data.config.date;
    }

    renderTable() {
        const table = document.createElement('table');
        table.className = 'visual-grid';

        // 1. ساخت هدر جدول
        let thead = `<thead><tr>`;
        // ستون ثابت دانش‌آموز
        thead += `<th class="col-student">نام دانش‌آموز</th>`;
        // ستون‌های سوالات (داینامیک)
        this.data.config.questions.forEach((q, index) => {
            // تولتیپ متن سوال
            thead += `<th title="${q.text}">س ${index + 1}</th>`;
        });
        // ستون نمره
        thead += `<th>نمره کل</th></tr></thead>`;

        // 2. ساخت بدنه جدول
        let tbody = `<tbody>`;
        this.data.results.forEach(student => {
            tbody += `<tr>`;
            
            // نام دانش‌آموز
            tbody += `
                <td class="col-student">
                    <div class="student-info">
                        <img src="${student.avatar}" class="st-avatar">
                        <span class="st-name">${student.student_name}</span>
                    </div>
                </td>
            `;

            // سلول‌های نشانگر (Visual Indicators)
            student.answers.forEach(status => {
                const indicator = this.getIndicatorHTML(status);
                tbody += `<td><div class="indicator-cell">${indicator}</div></td>`;
            });

            // نمره کل
            tbody += `<td class="col-score">${student.total_score}</td>`;
            
            tbody += `</tr>`;
        });
        tbody += `</tbody>`;

        table.innerHTML = thead + tbody;
        this.container.appendChild(table);
    }

    // نگاشت وضعیت به HTML طبق JSON
    getIndicatorHTML(status) {
        const config = {
            'correct': { class: 'bg-green-500', icon: 'fa-check', title: 'پاسخ صحیح' },
            'wrong':   { class: 'bg-red-500', icon: 'fa-xmark', title: 'پاسخ اشتباه' },
            'partial': { class: 'bg-yellow-400', icon: 'fa-minus', title: 'نمره ناقص' },
            'skipped': { class: 'circle_outline', icon: 'fa-minus', title: 'پاسخ داده نشده' }
        };

        const style = config[status] || config['skipped'];

        return `
            <div class="status-dot ${style.class}" title="${style.title}">
                <i class="fa-solid ${style.icon}"></i>
            </div>
        `;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new MatrixRenderer('matrix-container');
});