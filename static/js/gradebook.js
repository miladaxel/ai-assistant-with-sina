document.addEventListener('DOMContentLoaded', () => {
    
    // 1. شبیه‌سازی دیتای دریافتی از سرور (همان JSON شما)
    const gradeData = {
        columns: [
            { id: "row_num", header: "شماره", width: "50px", is_fixed: true },
            { id: "full_name", header: "نام و نام خانوادگی", width: "180px", is_fixed: true },
            { id: "father_name", header: "نام پدر", width: "100px", is_fixed: true },
            { id: "exam_01", header: "آزمون مهر", sub_header: "1403/07/15", width: "100px", type: "score" },
            { id: "exam_02", header: "آزمون آبان", sub_header: "1403/08/20", width: "100px", type: "score" },
            { id: "exam_03", header: "میان‌ترم", sub_header: "1403/10/10", width: "100px", type: "score", is_major: true },
            // برای تست اسکرول چند تا ستون اضافه میکنم
            { id: "exam_04", header: "آزمون دی", sub_header: "1403/10/25", width: "100px", type: "score" },
            { id: "exam_05", header: "آزمون بهمن", sub_header: "1403/11/05", width: "100px", type: "score" }
        ],
        rows: [
            {
                student_id: "st_101",
                data: { row_num: 1, full_name: "آرمان آریا", father_name: "بیژن", exam_01: 18, exam_02: 19.5, exam_03: 17, exam_04: 15, exam_05: 16 }
            },
            {
                student_id: "st_102",
                data: { row_num: 2, full_name: "بهرام بهرامی", father_name: "کامران", exam_01: 15, exam_02: 14, exam_03: 16.5, exam_04: 12, exam_05: 14 }
            },
             {
                student_id: "st_103",
                data: { row_num: 3, full_name: "سارا احمدی", father_name: "علی", exam_01: 20, exam_02: 20, exam_03: 19, exam_04: 19.5, exam_05: 20 }
            }
        ],
        summary: {
            exam_01: { avg: 17.6, max: 20, min: 15 },
            exam_02: { avg: 17.8, max: 20, min: 14 },
            exam_03: { avg: 17.5, max: 19, min: 16.5 },
            exam_04: { avg: 15.5, max: 19.5, min: 12 },
            exam_05: { avg: 16.6, max: 20, min: 14 }
        }
    };

    renderGradebook(gradeData);
});

function renderGradebook(data) {
    const table = document.getElementById('gradeTable');
    const thead = table.querySelector('thead');
    const tbody = table.querySelector('tbody');
    const tfoot = table.querySelector('tfoot');

    // متغیر برای محاسبه فاصله از راست (برای Sticky ها)
    let accumulatedRight = 0;

    // --- 1. ساخت هدر (Thead) ---
    const headerRow = document.createElement('tr');
    
    data.columns.forEach(col => {
        const th = document.createElement('th');
        
        // محتوای هدر
        let content = `<span>${col.header}</span>`;
        if (col.sub_header) {
            content += `<span class="sub-header" style="display:block; font-size:0.75rem; font-weight:normal; margin-top:4px;">${col.sub_header}</span>`;
        }
        th.innerHTML = `<div class="th-content">${content}</div>`;

        // لاجیک Sticky و استایل‌ها
        if (col.is_fixed) {
            th.classList.add('sticky-col');
            th.style.right = `${accumulatedRight}px`;
            th.style.width = col.width;
            th.style.zIndex = '20'; // اولویت بالا برای هدر ثابت
            
            // اضافه کردن عرض این ستون به متغیر برای ستون بعدی
            // عدد را از رشته "50px" استخراج می‌کنیم
            accumulatedRight += parseInt(col.width);
        } else {
             th.style.minWidth = col.width; // عرض ثابت برای ستون‌های اسکرول‌خور
        }

        if (col.is_major) {
            th.classList.add('major-exam'); // رنگ متفاوت برای امتحان مهم
        }

        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);


    // --- 2. ساخت بدنه (Tbody) ---
    data.rows.forEach(rowItem => {
        const tr = document.createElement('tr');
        
        // ریست کردن محاسبه‌گر برای هر ردیف
        let rowAccumulatedRight = 0;

        data.columns.forEach(col => {
            const td = document.createElement('td');
            const cellData = rowItem.data[col.id] || '-'; // اگر نمره نداشت خط تیره بذار

            td.textContent = cellData;

            // لاجیک Sticky برای سلول‌ها
            if (col.is_fixed) {
                td.classList.add('sticky-col');
                td.style.right = `${rowAccumulatedRight}px`;
                td.style.width = col.width;
                td.style.zIndex = '5';
                
                // استایل خاص برای نام‌ها
                if(col.id === 'full_name') td.style.fontWeight = 'bold';
                if(col.id === 'father_name') td.style.color = '#777';

                rowAccumulatedRight += parseInt(col.width);
            }

            if (col.is_major) {
                td.classList.add('major-cell');
            }

            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });


    // --- 3. ساخت فوتر (Tfoot) ---
    const footerRow = document.createElement('tr');
    let footerAccumulatedRight = 0;

    data.columns.forEach(col => {
        const td = document.createElement('td');

        // اگر ستون نمره است، خلاصه را نشان بده
        if (data.summary[col.id]) {
            const stats = data.summary[col.id];
            td.innerHTML = `
                <div class="summary-cell" style="display:flex; flex-direction:column; gap:2px; font-size:0.75rem;">
                    <div style="color:#64B5F6">∅ ${stats.avg}</div>
                    <div style="color:#81C784">↑ ${stats.max}</div>
                    <div style="color:#E57373">↓ ${stats.min}</div>
                </div>
            `;
        } else if (col.id === 'full_name') {
            td.textContent = "جمع‌بندی";
            td.style.fontWeight = "bold";
        }

        // لاجیک Sticky برای فوتر
        if (col.is_fixed) {
            td.classList.add('sticky-col');
            td.style.right = `${footerAccumulatedRight}px`;
            td.style.width = col.width;
            td.style.zIndex = '20'; // اولویت بالا مثل هدر
            td.style.backgroundColor = '#37474F'; // رنگ زمینه فوتر برای پوشاندن زیرین

            footerAccumulatedRight += parseInt(col.width);
        }

        footerRow.appendChild(td);
    });
    tfoot.appendChild(footerRow);
}