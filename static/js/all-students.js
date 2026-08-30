// js/all-students.js
import { allStudentsData } from "./store.js";

class StudentListManager {
  constructor() {
    this.data = allStudentsData;
    this.tableBody = document.getElementById("tableBody");
    this.searchInput = document.getElementById("studentSearch");
    this.noResultMsg = document.getElementById("no-result");

    this.init();
  }

  init() {
    // رندر اولیه همه داده‌ها
    this.renderTable(this.data);

    // فعال‌سازی جستجو
    this.searchInput.addEventListener("input", (e) => {
      this.handleSearch(e.target.value);
    });
  }

  renderTable(items) {
    this.tableBody.innerHTML = ""; // پاک کردن جدول

    if (items.length === 0) {
      this.noResultMsg.classList.remove("hidden");
      return;
    } else {
      this.noResultMsg.classList.add("hidden");
    }

    items.forEach((student) => {
      const tr = document.createElement("tr");

      // انتخاب کلاس رنگی برای بج
      const badgeClass = `badge-${student.grade_color}`; // badge-blue, badge-purple, ...

      // ...
      tr.innerHTML = `
<td style="text-align:center; color:#94a3b8;">${student.row_number}</td>
<td style="font-weight:bold;">${student.full_name}</td>
<td style="text-align:left;">
    <span class="grade-badge badge-${student.grade_color}">${student.grade_label}</span>
</td>
`;
      // ...

      // قابلیت کلیک روی سطر (مثلاً رفتن به جزئیات دانش‌آموز)
      tr.addEventListener("click", () => {
        // window.location.href = `student-profile.html?id=${student.id}`;
        alert(`نمایش پروفایل: ${student.full_name}`);
      });

      this.tableBody.appendChild(tr);
    });
  }

  handleSearch(query) {
    const searchTerm = query.trim().toLowerCase();

    // فیلتر کردن آرایه اصلی
    const filteredData = this.data.filter((student) =>
      student.full_name.toLowerCase().includes(searchTerm)
    );

    this.renderTable(filteredData);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new StudentListManager();
});
