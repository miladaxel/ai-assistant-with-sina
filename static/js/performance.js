// js/performance.js
import { examPerformanceData } from './store.js';

class PerformanceManager {
    constructor() {
        this.data = examPerformanceData;
        this.questionsList = document.getElementById('questions-list');
        this.gradesList = document.getElementById('grades-list');
        this.chartContainer = document.getElementById('chart-bars');
        this.init();
    }

    init() {
        this.renderQuestions();
        this.renderGrades();
        this.renderChart();
    }

    renderQuestions() {
        if(!this.questionsList) return;
        
        this.questionsList.innerHTML = this.data.questions.map(q => `
            <div class="question-card" onclick="alert('نمایش جزئیات سوال ${q.num}')">
                <div class="q-badge">${q.num}</div>
                <div class="q-text">${q.text}</div>
                <div style="font-size:0.75rem; color:${parseInt(q.correct_rate) > 70 ? '#16a34a' : '#ef4444'}">
                    ${q.correct_rate} صحیح
                </div>
                <i class="fa-solid fa-chevron-left" style="color:#cbd5e1; margin-right:auto;"></i>
            </div>
        `).join('');
    }

    renderGrades() {
        if(!this.gradesList) return;

        this.gradesList.innerHTML = this.data.students.map(st => `
            <div class="rank-row" onclick="window.location.href='student-exam-result.html'">
                <div class="rank-num">${st.rank}</div>
                <div class="rank-name">${st.name}</div>
                <div class="rank-score">${st.score}</div>
                <i class="fa-solid fa-chevron-left" style="color:#cbd5e1; font-size:0.8rem; margin-right:10px;"></i>
            </div>
        `).join('');
    }

    renderChart() {
        if(!this.chartContainer) return;

        // رندر نمودار میله‌ای ساده
        this.chartContainer.innerHTML = this.data.distribution.map(d => `
            <div class="chart-bar" style="height: ${d.height}" title="${d.count} نفر">
                <span class="bar-val">${d.count}</span>
                <span class="bar-label">${d.label}</span>
            </div>
        `).join('');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new PerformanceManager();
});