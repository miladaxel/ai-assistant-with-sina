// js/notes.js
import { teacherClasses, allStudentsData } from './store.js'; // فرض بر این است allStudentsData وجود دارد

let currentTargetType = 'class';
let selectedStudent = null;

// 1. مقداردهی اولیه لیست کلاس‌ها
const classSelect = document.getElementById('classSelect');
if(classSelect) {
    teacherClasses.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.id;
        opt.innerText = c.name;
        classSelect.appendChild(opt);
    });
}

// 2. تغییر نوع مخاطب (Tab Switching)
window.setTargetType = (type) => {
    currentTargetType = type;
    
    // آپدیت UI دکمه‌ها
    document.querySelectorAll('.segment-opt').forEach(el => {
        el.classList.toggle('active', el.dataset.value === type);
    });

    // نمایش سکشن مربوطه
    if (type === 'class') {
        document.getElementById('section-class').classList.add('visible');
        document.getElementById('section-student').classList.remove('visible');
    } else {
        document.getElementById('section-class').classList.remove('visible');
        document.getElementById('section-student').classList.add('visible');
    }
};

// 3. مودال دانش‌آموزان
window.openStudentModal = () => {
    document.getElementById('studentModal').classList.add('open');
    renderStudentList(allStudentsData || []);
};

window.closeStudentModal = () => {
    document.getElementById('studentModal').classList.remove('open');
};

const modalList = document.getElementById('modalList');
const searchInput = document.getElementById('modalSearch');

// رندر لیست در مودال
function renderStudentList(list) {
    modalList.innerHTML = list.map(st => `
        <div class="modal-item" onclick="selectStudent('${st.id}', '${st.full_name}')">
            <img src="https://ui-avatars.com/api/?name=${st.full_name}&background=random" style="width:36px; height:36px; border-radius:50%;">
            <div>
                <div style="font-weight:bold; font-size:0.9rem;">${st.full_name}</div>
                <div style="font-size:0.8rem; color:#94a3b8;">${st.grade_label || 'دانش‌آموز'}</div>
            </div>
        </div>
    `).join('');
}

// جستجو در مودال
if(searchInput) {
    searchInput.addEventListener('input', (e) => {
        const val = e.target.value.toLowerCase();
        const filtered = (allStudentsData || []).filter(s => s.full_name.toLowerCase().includes(val));
        renderStudentList(filtered);
    });
}

// 4. انتخاب دانش‌آموز
window.selectStudent = (id, name) => {
    selectedStudent = { id, name };
    
    // آپدیت UI
    document.getElementById('student-empty-state').style.display = 'none';
    document.getElementById('student-selected-state').style.display = 'flex';
    document.getElementById('sel-st-name').innerText = name;
    document.getElementById('sel-st-avatar').src = `https://ui-avatars.com/api/?name=${name}&background=random`;
    
    closeStudentModal();
};

window.clearStudentSelection = () => {
    selectedStudent = null;
    document.getElementById('student-empty-state').style.display = 'block';
    document.getElementById('student-selected-state').style.display = 'none';
};

// 5. ثبت نهایی
window.submitNote = () => {
    const text = document.getElementById('noteText').value;
    
    if(!text) {
        alert('لطفاً متن یادداشت را وارد کنید.');
        return;
    }

    if(currentTargetType === 'class' && !classSelect.value) {
        alert('لطفاً یک کلاس را انتخاب کنید.');
        return;
    }

    if(currentTargetType === 'student' && !selectedStudent) {
        alert('لطفاً یک دانش‌آموز را انتخاب کنید.');
        return;
    }

    // شبیه‌سازی ذخیره
    alert('یادداشت با موفقیت ثبت شد!');
    window.location.href = 'notes-history.html';
};