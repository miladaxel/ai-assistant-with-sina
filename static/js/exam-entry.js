// js/exam-entry.js
import { examEntryData } from './store.js';

export class ExamMatrixManager {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.data = examEntryData;
        this.init();
    }

    init() {
        this.renderTable();
        this.attachGlobalEvents();
    }

    renderTable() {
        // ساخت هدر جدول
        let headersHtml = '';
        this.data.columns_schema.forEach(col => {
            let className = '';
            // نگاشت pinned به کلاس‌های CSS
            if (col.pinned === 'start') className = 'col-fixed-start'; // نام دانش‌آموز (راست)
            if (col.pinned === 'end') className = 'col-fixed-end';     // نمره کل (چپ)
            
            // اضافه کردن Max Score به هدر برای اطلاع معلم
            let subText = col.meta ? `<div style="font-size:0.7rem; color:#888; font-weight:normal">(max: ${col.meta.max_score})</div>` : '';
            
            headersHtml += `<th class="${className}" data-col-id="${col.id}">${col.label} ${subText}</th>`;
        });

        // ساخت ردیف‌ها
        let rowsHtml = '';
        this.data.rows_data_example.forEach(student => {
            let cellsHtml = '';
            let totalScore = 0;

            this.data.columns_schema.forEach(col => {
                // 1. ستون نام دانش‌آموز (ثابت راست)
                if (col.type === 'fixed_column') {
                    cellsHtml += `<td class="col-fixed-start">${student.student_name}</td>`;
                } 
                // 2. ستون نمره کل (ثابت چپ - محاسبه شده)
                else if (col.type === 'calculated_column') {
                    cellsHtml += `<td class="col-fixed-end"><span class="total-cell" id="total_${student.student_id}">0</span></td>`;
                } 
                // 3. ستون‌های سوال (ورودی)
                else {
                    const max = col.meta.max_score;
                    const val = student.answers[col.id] || 0; // خواندن نمره قبلی یا صفر
                    totalScore += parseFloat(val);

                    cellsHtml += `
                        <td>
                            <div class="cell-wrapper">
                                <input type="number" 
                                    class="score-input" 
                                    data-max="${max}" 
                                    data-row="${student.student_id}" 
                                    data-col="${col.id}"
                                    value="${val}" 
                                    min="0" 
                                    max="${max}"
                                    step="0.25">
                                <button class="dropdown-trigger" tabindex="-1">▼</button>
                            </div>
                        </td>
                    `;
                }
            });

            rowsHtml += `<tr data-row-id="${student.student_id}">${cellsHtml}</tr>`;
        });

        this.container.innerHTML = `
            <div class="matrix-header-info">
                <h2>${this.data.label} - ${this.data.config.exam_id}</h2>
                <button class="btn btn-primary" id="saveBtn">ثبت نمرات</button>
            </div>
            <div class="matrix-container">
                <table class="exam-table">
                    <thead><tr>${headersHtml}</tr></thead>
                    <tbody>${rowsHtml}</tbody>
                </table>
            </div>
            <div id="quickMenu" class="quick-menu"></div>
        `;

        // محاسبه اولیه جمع کل
        this.recalculateAllTotals();
        // رنگ‌بندی اولیه
        this.colorizeAllInputs();
    }

    attachGlobalEvents() {
        const table = this.container.querySelector('table');
        const quickMenu = document.getElementById('quickMenu');

        // 1. مدیریت ورودی (Input Event) برای محاسبه و رنگ
        table.addEventListener('input', (e) => {
            if (e.target.classList.contains('score-input')) {
                this.handleInput(e.target);
            }
        });

        // 2. مدیریت نویگیشن کیبورد (Enter/Arrow Keys)
        table.addEventListener('keydown', (e) => {
            if (e.target.classList.contains('score-input')) {
                this.handleNavigation(e, e.target);
            }
        });

        // 3. مدیریت دکمه دراپ‌داون و کلیک راست
        table.addEventListener('click', (e) => {
            if (e.target.classList.contains('dropdown-trigger')) {
                const input = e.target.previousElementSibling;
                this.showQuickMenu(e, input);
            }
        });
        
        // بستن منو با کلیک بیرون
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.quick-menu') && !e.target.closest('.dropdown-trigger')) {
                quickMenu.classList.remove('active');
            }
        });
    }

    handleInput(input) {
        const max = parseFloat(input.dataset.max);
        let val = parseFloat(input.value);

        // Validation: نمره نباید از Max بیشتر باشد
        if (val > max) {
            val = max;
            input.value = max;
        }
        if (isNaN(val) || val < 0) {
            val = 0;
            // input.value = 0; // اختیاری: اگر خالی کرد صفر شود
        }

        // 1. تغییر رنگ
        this.colorizeInput(input, val, max);

        // 2. آپدیت جمع کل ردیف
        const rowId = input.dataset.row;
        this.updateRowTotal(rowId);
    }

    colorizeInput(input, val, max) {
        input.classList.remove('status-correct', 'status-wrong');
        if (val === max) input.classList.add('status-correct');
        else if (val === 0) input.classList.add('status-wrong');
    }

    colorizeAllInputs() {
        this.container.querySelectorAll('.score-input').forEach(input => {
            this.handleInput(input);
        });
    }

    updateRowTotal(rowId) {
        const row = this.container.querySelector(`tr[data-row-id="${rowId}"]`);
        let sum = 0;
        row.querySelectorAll('.score-input').forEach(inp => {
            sum += parseFloat(inp.value || 0);
        });
        
        // نمایش در سلول آخر
        const totalCell = row.querySelector(`#total_${rowId}`);
        if(totalCell) totalCell.textContent = sum;
    }

    recalculateAllTotals() {
        this.data.rows_data_example.forEach(row => this.updateRowTotal(row.student_id));
    }

    // --- منطق نویگیشن حرفه‌ای ---
    handleNavigation(e, currentInput) {
        const currentRow = currentInput.closest('tr');
        const currentCell = currentInput.closest('td');
        const allRows = Array.from(this.container.querySelectorAll('tbody tr'));
        const currentRowIndex = allRows.indexOf(currentRow);
        const cellsInRow = Array.from(currentRow.children);
        const currentCellIndex = cellsInRow.indexOf(currentCell);

        if (e.key === 'Enter') {
            e.preventDefault();
            // حرکت به پایین (همان ستون، ردیف بعدی)
            if (currentRowIndex < allRows.length - 1) {
                const nextRow = allRows[currentRowIndex + 1];
                const targetCell = nextRow.children[currentCellIndex];
                const targetInput = targetCell.querySelector('input');
                if (targetInput) targetInput.focus();
            }
        } 
        // برای حرکت با تب نیازی به کد خاصی نیست چون رفتار پیش‌فرض مرورگر درست است
    }

    showQuickMenu(e, input) {
        const max = parseFloat(input.dataset.max);
        const quickMenu = document.getElementById('quickMenu');
        
        // گزینه‌های منو
        quickMenu.innerHTML = `
            <div class="quick-item" onclick="setScore(${max})">✅ صحیح (${max})</div>
            <div class="quick-item" onclick="setScore(${max/2})">⚠️ نصف (${max/2})</div>
            <div class="quick-item" onclick="setScore(0)">❌ غلط (0)</div>
        `;

        // پوزیشن منو
        const rect = e.target.getBoundingClientRect();
        quickMenu.style.top = `${rect.bottom + window.scrollY}px`;
        quickMenu.style.left = `${rect.left + window.scrollX}px`;
        quickMenu.classList.add('active');

        // تابع کمکی که به window وصل می‌شود تا از توی HTML string کار کند
        window.setScore = (score) => {
            input.value = score;
            input.focus(); // تریگر کردن ایونت‌ها
            // دستی تریگر کردن ایونت input
            const event = new Event('input', { bubbles: true });
            input.dispatchEvent(event);
            quickMenu.classList.remove('active');
        };
    }
}