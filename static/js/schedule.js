// js/schedule.js
import { weeklyScheduleData, availableClasses } from './store.js';

// تعریف روزها و زنگ‌ها
const daysConfig = [
    { id: 'sat', label: 'شنبه' },
    { id: 'sun', label: 'یکشنبه' },
    { id: 'mon', label: 'دوشنبه' },
    { id: 'tue', label: 'سه‌شنبه' },
    { id: 'wed', label: 'چهارشنبه' },
    { id: 'thu', label: 'پنج‌شنبه' }
];

const slotsConfig = [
    "زنگ اول (۸:۰۰ - ۹:۳۰)",
    "زنگ دوم (۰۹:۳۰ - ۱۱:۰۰)",
    "زنگ سوم (۱۱:۰۰ - ۱۲:۳۰)",
    "زنگ چهارم (۱۲:۳۰ - ۱۴:۰۰)"
];

// متغیرهای وضعیت ویرایش
let currentEditTarget = { dayId: null, slotIndex: null };

class ScheduleManager {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.schedule = weeklyScheduleData;
        this.classes = availableClasses;
        this.init();
    }

    init() {
        this.renderSchedule();
        this.renderClassOptions();
    }

    // --- رندر کردن کل برنامه (Nested Loops) ---
    renderSchedule() {
        this.container.innerHTML = ''; // پاک کردن

        // حلقه اول: روی روزها
        daysConfig.forEach(day => {
            const dayData = this.schedule[day.id] || [null, null, null];
            
            // ساخت کانتینر روز
            const daySection = document.createElement('div');
            daySection.className = 'day-section';
            
            let slotsHtml = '';

            // حلقه دوم: روی زنگ‌ها (۳ بار)
            for (let i = 0; i < 3; i++) {
                const slotData = dayData[i];
                const timeLabel = slotsConfig[i];

                if (slotData) {
                    // حالت پر (Filled)
                    slotsHtml += `
                        <div class="slot-container">
                            <div class="slot-label">${timeLabel}</div>
                            <div class="slot-filled" onclick="window.openClassModal('${day.id}', ${i})">
                                <div class="class-name">${slotData.name}</div>
                            </div>
                        </div>
                    `;
                } else {
                    // حالت خالی (Empty - Dashed)
                    slotsHtml += `
                        <div class="slot-container">
                            <div class="slot-label">${timeLabel}</div>
                            <div class="slot-empty" onclick="window.openClassModal('${day.id}', ${i})">
                                <i class="fa-solid fa-plus-circle empty-icon"></i>
                                <span>افزودن کلاس</span>
                            </div>
                        </div>
                    `;
                }
            }

            daySection.innerHTML = `
                <div class="day-header">${day.label}</div>
                <div style="display:flex; flex-direction:column; gap:15px;">
                    ${slotsHtml}
                </div>
            `;
            
            this.container.appendChild(daySection);
        });
    }

    // --- رندر لیست کلاس‌ها در مودال ---
    renderClassOptions() {
        const list = document.getElementById('classes-list');
        list.innerHTML = this.classes.map(cls => `
            <div class="class-option" onclick="window.saveClass('${cls.id}')">
                <div style="font-weight:bold">${cls.name}</div>
                <div style="font-size:0.8rem; color:#64748b">${cls.location}</div>
            </div>
        `).join('') + `
            <div class="class-option" onclick="window.saveClass(null)" style="border-style:dashed; text-align:center; color:#ef4444;">
                <i class="fa-solid fa-trash"></i> حذف کلاس (خالی کردن)
            </div>
        `;
    }

    // باز کردن مودال
    openModal(dayId, slotIndex) {
        currentEditTarget = { dayId, slotIndex };
        document.getElementById('classSelectModal').classList.add('open');
    }

    // ذخیره کلاس انتخاب شده
    saveClass(classId) {
        const { dayId, slotIndex } = currentEditTarget;
        
        if (classId) {
            // پیدا کردن اطلاعات کامل کلاس از آرایه availableClasses
            const classInfo = this.classes.find(c => c.id === classId);
            // آپدیت دیتا
            this.schedule[dayId][slotIndex] = {
                class_id: classInfo.id,
                name: classInfo.name,
                location: classInfo.location
            };
        } else {
            // حذف کلاس (null کردن)
            this.schedule[dayId][slotIndex] = null;
        }

        // بستن مودال و رندر مجدد
        document.getElementById('classSelectModal').classList.remove('open');
        this.renderSchedule();
    }
}

// Global functions
window.closeModal = () => document.getElementById('classSelectModal').classList.remove('open');
window.toggleEditMode = () => alert('حالت ویرایش فعال شد! روی هر باکس کلیک کنید.');

document.addEventListener('DOMContentLoaded', () => {
    const manager = new ScheduleManager('schedule-container');
    
    // اکسپوز کردن توابع به ویندو
    window.openClassModal = (d, i) => manager.openModal(d, i);
    window.saveClass = (id) => manager.saveClass(id);
});