// دیتای شبیه‌سازی شده (طبق JSON شما)
const studentsData = [
  {
    id: "st_101",
    name: "رضا علوی",
    father: "حسن",
    status: "pending", // نیاز به تصحیح
    avatar: "https://via.placeholder.com/150",
  },
  {
    id: "st_102",
    name: "مینا کریمی",
    father: "علی",
    status: "completed", // نمره دارد
    score: "۱۸/۲۰",
    avatar: "https://via.placeholder.com/150",
  },
  {
    id: "st_103",
    name: "سینا راد",
    father: "محمد",
    status: "pending",
    avatar: "https://via.placeholder.com/150",
  },
];

// --- تابع ۱: تولید داینامیک سوالات ---
// متصل به input[type=number] در HTML
function generateQuestions() {
  const total = document.getElementById("totalQuestions").value;
  const container = document.getElementById("questionsContainer");

  // پاک کردن قبلی‌ها
  container.innerHTML = "";

  if (total > 0) {
    for (let i = 1; i <= total; i++) {
      // ساخت HTML برای هر ردیف سوال طبق row_template
      const div = document.createElement("div");
      div.className = "question-row";
      div.innerHTML = `
                <label>سوال شماره ${i}</label>
                <input type="number" value="1" min="1" placeholder="تعداد بخش‌ها">
            `;
      container.appendChild(div);
    }
  }
}

// --- تابع ۲: ذخیره تنظیمات و نمایش لیست (Action: on_save) ---
function saveAndLoadList() {
  const title = document.getElementById("examTitle").value;
  const total = document.getElementById("totalQuestions").value;

  if (!title || !total) {
    alert("لطفاً عنوان و تعداد سوالات را وارد کنید.");
    return;
  }

  // 1. بستن کارت تنظیمات (Collapse)
  const configCard = document.getElementById("configCard");
  configCard.classList.remove("expanded");
  configCard.classList.add("collapsed");

  // 2. نمایش بخش لیست دانش‌آموزان (Fade In)
  const gradingSection = document.getElementById("gradingSection");
  gradingSection.classList.remove("hidden");
  gradingSection.classList.add("active"); // تریگر انیمیشن CSS

  // 3. رندر کردن لیست دانش‌آموزان
  renderStudents();
}

// --- تابع ۳: برگشت به حالت ویرایش (Action: on_edit) ---
function toggleEditMode() {
  // باز کردن کارت تنظیمات
  const configCard = document.getElementById("configCard");
  configCard.classList.remove("collapsed");
  configCard.classList.add("expanded");

  // مخفی کردن لیست دانش‌آموزان (اختیاری - بسته به UX مورد نظر)
  // طبق JSON اشاره‌ای به مخفی شدن نشده، اما معمولا برای تمرکز بهتر مخفی می‌شود.
  // اینجا برای سادگی لیست را نگه می‌داریم یا می‌توانیم کلاس hidden را برگردانیم.
  // document.getElementById('gradingSection').classList.remove('active');
  // document.getElementById('gradingSection').classList.add('hidden');
}

// --- تابع ۴: ساختن کارت‌های دانش‌آموز ---
function renderStudents() {
  const listContainer = document.getElementById("studentListContainer");
  listContainer.innerHTML = ""; // پاکسازی

  studentsData.forEach((st) => {
    const row = document.createElement("div");
    row.className = "student-row";

    // تعیین دکمه سمت چپ بر اساس وضعیت (State Logic)
    let actionComponent = "";

    if (st.status === "pending") {
      // دکمه شروع تصحیح
      actionComponent = `
    <button class="btn-grading" onclick="openGradingModal('${st.id}', '${st.name}', '${st.avatar}')">
        <i class="fa-solid fa-pen-to-square"></i> شروع تصحیح
    </button>
`;
    } else if (st.status === "completed") {
      // بج نمره (غیر قابل کلیک)
      actionComponent = `
                <div class="score-badge">
                    <i class="fa-solid fa-circle-check"></i>
                    نمره: ${st.score}
                </div>
            `;
    }

    row.innerHTML = `
            <div class="student-info">
                <img src="${st.avatar}" class="avatar" alt="Avatar">
                <div>
                    <span class="st-name">${st.name}</span>
                    <span class="st-father">نام پدر: ${st.father}</span>
                </div>
            </div>

            <div class="grading-status">
                ${actionComponent}
            </div>
        `;

    listContainer.appendChild(row);
  });
}

// دیتای شبیه‌سازی شده سوالات (طبق JSON شما)
const gradingTemplate = {
  max_score: 20,
  questions: [
    {
      q_number: 1,
      title: "سوال اول (مبحث تابع)",
      parts: [
        { id: "q1_p1", label: "الف)", weight: 2.5 },
        { id: "q1_p2", label: "ب)", weight: 2.5 },
      ],
    },
    {
      q_number: 2,
      title: "سوال دوم (هندسه)",
      parts: [{ id: "q2_p1", label: "پاسخ کلی", weight: 5 }],
    },
  ],
};

// وضعیت نمرات فعلی (برای محاسبه هوشمند)
let currentGrades = {}; // مثلا: { 'q1_p1': 2.5, 'q1_p2': 0 }

// --- ۱. باز کردن مودال ---
// این تابع باید روی دکمه‌های "شروع تصحیح" در لیست دانش‌آموزان صدا زده شود
// مثال: onclick="openGradingModal('st_101', 'رضا علوی', '...jpg')"
function openGradingModal(studentId, studentName, avatarUrl) {
  // ریست کردن وضعیت
  currentGrades = {};
  document.getElementById("modalLiveScore").innerText = "0";

  // پر کردن اطلاعات هدر
  document.getElementById("modalStName").innerText = studentName;
  document.getElementById("modalAvatar").src = avatarUrl;

  // ساختن فرم سوالات
  renderGradingForm();

  // نمایش مودال
  const overlay = document.getElementById("gradingModalOverlay");
  overlay.classList.add("open");
}

// --- ۲. بستن مودال ---
function closeGradingModal() {
  document.getElementById("gradingModalOverlay").classList.remove("open");
}

// --- ۳. رندر کردن فرم سوالات ---
function renderGradingForm() {
  const container = document.getElementById("gradingQuestionsList");
  container.innerHTML = ""; // پاکسازی

  gradingTemplate.questions.forEach((q) => {
    // ساخت کارت سوال
    const card = document.createElement("div");
    card.className = "g-question-card";

    let partsHTML = "";
    q.parts.forEach((part) => {
      partsHTML += `
                <div class="g-part-row">
                    <span class="g-part-label">${part.label} <small style="color:#999">(${part.weight})</small></span>
                    
                    <div class="g-options-group">
                        <button class="g-opt-btn" onclick="ratePart('${part.id}', 'correct', ${part.weight}, this)">
                            <i class="fa-solid fa-check"></i>
                        </button>
                        <button class="g-opt-btn" onclick="ratePart('${part.id}', 'incorrect', ${part.weight}, this)">
                            <i class="fa-solid fa-xmark"></i>
                        </button>
                        <button class="g-opt-btn" onclick="ratePart('${part.id}', 'empty', ${part.weight}, this)">
                            <i class="fa-solid fa-minus"></i>
                        </button>
                    </div>
                </div>
            `;
    });

    card.innerHTML = `
            <div class="g-q-title">${q.title}</div>
            ${partsHTML}
        `;
    container.appendChild(card);
  });
}

// --- ۴. منطق نمره دهی (Core Logic) ---
function ratePart(partId, type, weight, btnElement) {
  // الف) مدیریت استایل دکمه‌ها
  // پیدا کردن دکمه‌های هم‌گروه (Sibling buttons)
  const parentGroup = btnElement.parentElement;
  const buttons = parentGroup.querySelectorAll(".g-opt-btn");

  // حذف کلاس‌های اکتیو از همه دکمه‌های این ردیف
  buttons.forEach((btn) => {
    btn.classList.remove("active-correct", "active-incorrect", "active-empty");
  });

  // اضافه کردن کلاس اکتیو به دکمه کلیک شده
  if (type === "correct") btnElement.classList.add("active-correct");
  else if (type === "incorrect") btnElement.classList.add("active-incorrect");
  else btnElement.classList.add("active-empty");

  // ب) محاسبه نمره
  // اگر صحیح بود نمره کامل، در غیر این صورت 0
  const newScore = type === "correct" ? weight : 0;

  // ذخیره در آبجکت وضعیت
  currentGrades[partId] = newScore;

  // ج) آپدیت نمایشگر مجموع نمرات
  updateTotalScore();
}

function updateTotalScore() {
  // جمع کردن تمام مقادیر موجود در currentGrades
  let total = 0;
  for (let key in currentGrades) {
    total += currentGrades[key];
  }

  // نمایش با انیمیشن ساده
  document.getElementById("modalLiveScore").innerText = total;
}

// --- ۵. ثبت نهایی ---
function submitGrade() {
  // اینجا می‌توانید کد ارسال به سرور (Ajax) را بنویسید
  // فعلا فقط شبیه‌سازی می‌کنیم

  // تغییر دکمه به حالت لودینگ
  const btn = event.currentTarget;
  const originalText = btn.innerHTML;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> در حال ثبت...';

  setTimeout(() => {
    alert("نمره با موفقیت ثبت شد!");
    closeGradingModal();
    btn.innerHTML = originalText;

    // اینجا می‌توانید وضعیت دانش‌آموز را در لیست پشت سر آپدیت کنید (مثلا سبز کنید)
    // updateStudentStatusInList(...)
  }, 1000);
}
