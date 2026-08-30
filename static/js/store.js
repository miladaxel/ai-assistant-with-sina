// js/store.js
// ... (دیتای قبلی dashboard و classes) ...

export const examEntryData = {
    "tab_id": "manual_entry_matrix",
    "label": "ورود دستی نمرات",
    "config": {
      "exam_id": "EX_204",
      "total_questions": 3,
      "max_total_score": 10
    },
    "columns_schema": [
      // نکته: در حالت RTL، پین سمت "چپ" یعنی انتهای جدول و پین "راست" یعنی ابتدای جدول
      // برای راحتی، ما از کلاس‌های منطقی start و end استفاده می‌کنیم
      { "id": "student_info", "type": "fixed_column", "label": "نام دانش‌آموز", "pinned": "start" },
      { "id": "q1", "type": "question_column", "label": "س ۱", "meta": { "topic": "توابع", "max_score": 2 } },
      { "id": "q2", "type": "question_column", "label": "س ۲", "meta": { "topic": "مثلثات", "max_score": 4 } },
      { "id": "q3", "type": "question_column", "label": "س ۳", "meta": { "topic": "حد", "max_score": 4 } },
      { "id": "final_score", "type": "calculated_column", "label": "نمره کل", "pinned": "end" }
    ],
    "rows_data_example": [
      {
        "student_id": "st_101",
        "student_name": "علی رضایی",
        "answers": { "q1": 2, "q2": 0, "q3": 2.5 }
      },
      {
        "student_id": "st_102",
        "student_name": "محمد محمدی",
        "answers": { "q1": 1.5, "q2": 3, "q3": 4 }
      },
      {
          "student_id": "st_103",
          "student_name": "سارا امینی",
          "answers": { "q1": 0, "q2": 0, "q3": 0 }
      }
    ]
  };
  // js/store.js

// ... (دیتای قبلی) ...

export const classDetailData = {
  "info": {
      "id": "c_101",
      "title": "کلاس نهم توکل - زبان انگلیسی",
      "breadcrumb": [
          { "text": "لیست کلاس‌ها", "href": "classes.html" },
          { "text": localStorage.getItem("class")=="نهم - توکل"?"کلاس نهم توکل - زبان انگلیسی":"کلاس هفتم ۲", "href": "#", "active": true }
      ]
  },
  "students": [
        {
          "id": "st_1",
          "name": "امیرحسین آلبوعطوی",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Amirhossein+Alboatvi&background=random"
        },
        {
          "id": "st_2",
          "name": "امیرحسین اسکندری",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Amirhossein+Eskandari&background=random"
        },
        {
          "id": "st_3",
          "name": "محمدامین امیدوار",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Mohammadamin+Omidvar&background=random"
        },
        {
          "id": "st_4",
          "name": "محمدحسین انصاری",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Mohammadhossein+Ansari&background=random"
        },
        {
          "id": "st_5",
          "name": "نیما انوری",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Nima+Anvari&background=random"
        },
        {
          "id": "st_6",
          "name": "امیرحسین اولادباغی",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Amirhossein+Oladbaghi&background=random"
        },
        {
          "id": "st_7",
          "name": "عرفان باوندی",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Erfan+Bavandi&background=random"
        },
        {
          "id": "st_8",
          "name": "آریا باوی",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Arya+Bavi&background=random"
        },
        {
          "id": "st_9",
          "name": "محمد بچاری زاده",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Mohammad+Bacharizadeh&background=random"
        },
        {
          "id": "st_10",
          "name": "محمدجواد بچاری عجمی",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Mohammadjavad+Bachari&background=random"
        },
        {
          "id": "st_11",
          "name": "شهاب بدوی",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Shahab+Badavi&background=random"
        },
        {
          "id": "st_12",
          "name": "سیدمحمد مهدی بنی هاشمی",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=SeyedMohammad+Banihashemi&background=random"
        },
        {
          "id": "st_13",
          "name": "امیرحسین بهبهانی",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Amirhossein+Behbahani&background=random"
        },
        {
          "id": "st_14",
          "name": "طاها پاک نیت",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Taha+Pakniyat&background=random"
        },
        {
          "id": "st_15",
          "name": "علیرضا پولک کش",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Alireza+Polakkesh&background=random"
        },
        {
          "id": "st_16",
          "name": "ایلیا حردانی",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Iliya+Hardani&background=random"
        },
        {
          "id": "st_17",
          "name": "محمدجواد حسینی",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Mohammadjavad+Hosseini&background=random"
        },
        {
          "id": "st_18",
          "name": "رضا حسینی فخر",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Reza+HosseiniFakhr&background=random"
        },
        {
          "id": "st_19",
          "name": "محمدمتین حیدری",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Mohammadmatin+Heydari&background=random"
        },
        {
          "id": "st_20",
          "name": "حسین خوش اندام",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Hossein+Khoshandam&background=random"
        },
        {
          "id": "st_21",
          "name": "مهدی خیام زاده سواری نژاد",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Mehdi+Khayamzadeh&background=random"
        },
        {
          "id": "st_22",
          "name": "علی دوستانی فر",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Ali+Doostanifar&background=random"
        },
        {
          "id": "st_23",
          "name": "صدرا سپهری",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Sadra+Sepehri&background=random"
        },
        {
          "id": "st_24",
          "name": "حسین شجاع",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Hossein+Shoja&background=random"
        },
        {
          "id": "st_25",
          "name": "محمدرضا شریعت",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Mohammadreza+Shariat&background=random"
        },
        {
          "id": "st_26",
          "name": "علی اکبر شریفی اصیل",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Aliakbar+Sharifi&background=random"
        },
        {
          "id": "st_27",
          "name": "امیرعلی شفائیان",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Amirali+Shafaian&background=random"
        },
        {
          "id": "st_28",
          "name": "حسین صادقی پاک",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Hossein+Sadeghi&background=random"
        },
        {
          "id": "st_29",
          "name": "محمد صالحی",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Mohammad+Salehi&background=random"
        },
        {
          "id": "st_30",
          "name": "پرهام ضامن دوست",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Parham+Zamendoost&background=random"
        },
        {
          "id": "st_31",
          "name": "حسین طاهری نیا",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Hossein+Taherinia&background=random"
        },
        {
          "id": "st_32",
          "name": "محمدرضا عچرش",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Mohammadreza+Ochrash&background=random"
        },
        {
          "id": "st_33",
          "name": "محمدعلی عیدانی",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Mohammadali+Eidani&background=random"
        },
        {
          "id": "st_34",
          "name": "ابوالفضل قانعیان پور",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Abolfazl+Ghaneian&background=random"
        },
        {
          "id": "st_35",
          "name": "ابوالفضل قریشوندی",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Abolfazl+Ghoreishvandi&background=random"
        },
        {
          "id": "st_36",
          "name": "شهاب قنواتی محمدی",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Shahab+Ghanavati&background=random"
        },
        {
          "id": "st_37",
          "name": "میلاد کاشی ساز",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Milad+Kashisaz&background=random"
        },
        {
          "id": "st_38",
          "name": "سیدبنیامین کرمی",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Seyedbenyamin+Karami&background=random"
        },
        {
          "id": "st_39",
          "name": "محمدسجاد گزنی",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Mohammadsajad+Gazni&background=random"
        },
        {
          "id": "st_40",
          "name": "امیرعباس لامی نژاد",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Amirabbas+Laminejad&background=random"
        },
        {
          "id": "st_41",
          "name": "سیدمحمدعلی محفوظیان نژاد",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Seyedmohammadali+Mahfoozian&background=random"
        },
        {
          "id": "st_42",
          "name": "کاوه محمدیان",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Kaveh+Mohammadian&background=random"
        },
        {
          "id": "st_43",
          "name": "آرین محمودی کمک",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Arian+Mahmoodi&background=random"
        },
        {
          "id": "st_44",
          "name": "عرفان مردان",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Erfan+Mardan&background=random"
        },
        {
          "id": "st_45",
          "name": "محمدحسین مطوری",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Mohammadhossein+Matoori&background=random"
        },
        {
          "id": "st_46",
          "name": "محمدمهدی ملک",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Mohammadmahdi+Malek&background=random"
        },
        {
          "id": "st_47",
          "name": "عبدالله منصوریان",
          "class": "هفتم - ۲",
          "avatar": "https://ui-avatars.com/api/?name=Abdollah+Mansourian&background=random"
        },
        {
          "id": "st_48",
          "name": "امیرحسین منظری",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Amirhossein+Manzari&background=random"
        },
        {
          "id": "st_49",
          "name": "پارسا مهرجو",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Parsa+Mehrjoo&background=random"
        },
        {
          "id": "st_50",
          "name": "امیرمحمد وفائیان",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Amirmohammad+Vafaian&background=random"
        },
        {
          "id": "st_51",
          "name": "ماهان یاسین زاده",
          "class": "نهم - توکل",
          "avatar": "https://ui-avatars.com/api/?name=Mahan+Yasinzadeh&background=random"
        }
  ],
  "exams": [
    { 
        "id": "ex_1", 
        "title": "آزمون زبان انگلیسی - تعیین سطح", 
        "class": "نهم - توکل", 
        "date": "۱۴۰۴/۰۹/۲۵", 
        "status": "closed", 
        "status_label": "برگزار شده", 
        "score_avg": 17.5 
      },
      { 
        "id": "ex_2", 
        "title": "آزمون زبان انگلیسی - شخصی‌سازی شده میانی", 
        "class": "نهم - توکل", 
        "date": "۱۴۰۴/۱۰/۰۲", 
        "status": "pending", 
        "status_label": "در انتظار برگزاری", 
        "score_avg": null 
      },
      { 
        "id": "ex_3", 
        "title": "آزمون زبان انگلیسی - نهایی", 
        "class": "نهم - توکل", 
        "date": "۱۴۰۴/۱۰/۰۹", 
        "status": "pending", 
        "status_label": "در انتظار برگزاری", 
        "score_avg": null 
      },
      { 
        "id": "ex_1", 
        "title": "آزمون زبان انگلیسی - تعیین سطح", 
        "class": "هفتم - ۲", 
        "date": "۱۴۰۴/۰۹/۲۵", 
        "status": "closed", 
        "status_label": "برگزار شده", 
        "score_avg": 17.5 
      },
      { 
        "id": "ex_2", 
        "title": "آزمون زبان انگلیسی - شخصی‌سازی شده میانی", 
        "class": "هفتم - ۲", 
        "date": "۱۴۰۴/۱۰/۰۲", 
        "status": "pending", 
        "status_label": "در انتظار برگزاری", 
        "score_avg": null 
      },
      { 
        "id": "ex_3", 
        "title": "آزمون زبان انگلیسی - نهایی", 
        "class": "هفتم - ۲", 
        "date": "۱۴۰۴/۱۰/۰۹", 
        "status": "pending", 
        "status_label": "در انتظار برگزاری", 
        "score_avg": null 
      }
  ]
};

// js/store.js

// ... (دیتای قبلی) ...

export const examMatrixData = {
  "config": {
      "exam_title": "آزمون فصل اول - توابع",
      "date": "۱۴۰۲/۰۷/۱۰",
      "questions": [
          { "id": 1, "text": "دامنه تابع رادیکالی را بیابید." },
          { "id": 2, "text": "برد تابع درجه دوم زیر کدام است؟" },
          { "id": 3, "text": "آیا تابع مفروض یک‌به‌یک است؟" },
          { "id": 4, "text": "مقدار حد تابع در نقطه x=2" },
          { "id": 5, "text": "مشتق تابع در نقطه x=0" }
      ]
  },
  "results": [
      {
          "student_name": "علی رضایی",
          "avatar": "https://ui-avatars.com/api/?name=Ali+Rezaei&background=random",
          "total_score": 18,
          "answers": ["correct", "correct", "wrong", "correct", "correct"]
      },
      {
          "student_name": "محمد محمدی",
          "avatar": "https://ui-avatars.com/api/?name=Mohammad+M&background=random",
          "total_score": 12,
          "answers": ["wrong", "partial", "wrong", "correct", "skipped"]
      },
      {
          "student_name": "سارا امینی",
          "avatar": "https://ui-avatars.com/api/?name=Sara+Amini&background=random",
          "total_score": 20,
          "answers": ["correct", "correct", "correct", "correct", "correct"]
      },
      {
          "student_name": "کیارش رستمی",
          "avatar": "https://ui-avatars.com/api/?name=Kiarash+R&background=random",
          "total_score": 8,
          "answers": ["wrong", "wrong", "wrong", "partial", "wrong"]
      }
  ]
};

// js/store.js
// ... (کدهای قبلی) ...

// داده‌های ریز نمرات میان‌ترم برای هر دانش‌آموز
export const studentReports = {
  "st_1": { // علی رضایی
      "student_name": "علی رضایی",
      "exam_title": "میان‌ترم ریاضی - آذر ماه",
      "total_score": 18.5,
      "max_score": 20,
      "questions": [
          { "id": 1, "topic": "توابع", "status": "correct", "score": 4 },
          { "id": 2, "topic": "مثلثات", "status": "correct", "score": 3 },
          { "id": 3, "topic": "حد", "status": "wrong", "score": 0 }, // غلط
          { "id": 4, "topic": "پیوستگی", "status": "partial", "score": 1.5 }, // ناقص
          { "id": 5, "topic": "مشتق", "status": "correct", "score": 5 },
          { "id": 6, "topic": "کاربرد مشتق", "status": "correct", "score": 5 }
      ]
  },
  "st_2": { // محمد محمدی (برای تست)
      "student_name": "محمد محمدی",
      "exam_title": "میان‌ترم ریاضی - آذر ماه",
      "total_score": 12,
      "max_score": 20,
      "questions": [
          { "id": 1, "topic": "توابع", "status": "wrong", "score": 0 },
          { "id": 2, "topic": "مثلثات", "status": "wrong", "score": 0 },
          { "id": 3, "topic": "حد", "status": "correct", "score": 4 },
          { "id": 4, "topic": "پیوستگی", "status": "correct", "score": 4 },
          { "id": 5, "topic": "مشتق", "status": "partial", "score": 2 },
          { "id": 6, "topic": "کاربرد مشتق", "status": "partial", "score": 2 }
      ]
  }
};

// js/store.js

// ... (دیتای قبلی) ...

// لیست کلاس‌هایی که معلم دارد (برای انتخاب در مودال)
export const availableClasses = [
        { id: "c_101", name: "زبان انگلیسی - مقاومت", location: "کلاس ۱۰۱" },
        { id: "c_102", name: "زبان انگلیسی - هفتم ۲", location: "کلاس ۱۰۲" },
        { id: "c_103", name: "زبان انگلیسی - ایثار", location: "کلاس ۱۰۳" },
        { id: "c_104", name: "زبان انگلیسی - هشتم ۲", location: "کلاس ۱۰۴" },
        { id: "c_105", name: "زبان انگلیسی - نهم توکل", location: "کلاس ۱۰۵" },
        { id: "c_106", name: "زبان انگلیسی - نهم ۲", location: "کلاس ۱۰۶" },
    { id: "free", name: "ساعت آزاد / مطالعه", location: "دفتر معلمان" }
];

// داده‌های برنامه هفتگی (شنبه تا پنج‌شنبه)
export const weeklyScheduleData = {
    "sat": [
        { class_id: "c_101", name: "هفتم دو", location: "کلاس ۱۰۱" }, // زنگ ۱
        null, // زنگ ۲ خالی
        { class_id: "c_102", name: "نهم دو", location: "کلاس ۲۰۳" } // زنگ ۳
    ],
    "sun": [null, null, null],
    "mon": [
        null,
        null,
        null
    ],
    "tue": [null, null, null],
    "wed": [null, null, null],
    "thu": [null, null, null]
};

// js/store.js

// ... (دیتای قبلی) ...

// js/store.js

// ... (سایر دیتاها مثل teacherClasses و ... سر جای خود بمانند) ...

export const allStudentsData = [
    { id: "st_1", row_number: 1, full_name: "آلبوعطوی امیرحسین", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_2", row_number: 2, full_name: "اسکندری امیرحسین", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_3", row_number: 3, full_name: "امیدوار محمدامین", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_4", row_number: 4, full_name: "انصاری محمدحسین", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_5", row_number: 5, full_name: "انوری نیما", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_6", row_number: 6, full_name: "اولادباغی امیرحسین", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_7", row_number: 7, full_name: "باوندی عرفان", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_8", row_number: 8, full_name: "باوی آریا", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_9", row_number: 9, full_name: "بچاری زاده محمد", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_10", row_number: 10, full_name: "بچاری عجمی محمدجواد", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_11", row_number: 11, full_name: "بدوی شهاب", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_12", row_number: 12, full_name: "بنی هاشمی سیدمحمد مهدی", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_13", row_number: 13, full_name: "بهبهانی امیرحسین", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_14", row_number: 14, full_name: "پاک نیت طاها", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_15", row_number: 15, full_name: "پولک کش علیرضا", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_16", row_number: 16, full_name: "حردانی ایلیا", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_17", row_number: 17, full_name: "حسینی محمدجواد", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_18", row_number: 18, full_name: "حسینی فخر رضا", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_19", row_number: 19, full_name: "حیدری محمدمتین", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_20", row_number: 20, full_name: "خوش اندام حسین", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_21", row_number: 21, full_name: "خیام زاده سواری نژاد مهدی", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_22", row_number: 22, full_name: "دوستانی فر علی", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_23", row_number: 23, full_name: "سپهری صدرا", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_24", row_number: 24, full_name: "شجاع حسین", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_25", row_number: 25, full_name: "شریعت محمدرضا", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_26", row_number: 26, full_name: "شریفی اصیل علی اکبر", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_27", row_number: 27, full_name: "شفائیان امیرعلی", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_28", row_number: 28, full_name: "صادقی پاک حسین", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_29", row_number: 29, full_name: "صالحی محمد", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_30", row_number: 30, full_name: "ضامن دوست پرهام", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_31", row_number: 31, full_name: "طاهری نیا حسین", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_32", row_number: 32, full_name: "عچرش محمدرضا", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_33", row_number: 33, full_name: "عیدانی محمدعلی", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_34", row_number: 34, full_name: "قانعیان پور ابوالفضل", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_35", row_number: 35, full_name: "قریشوندی ابوالفضل", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_36", row_number: 36, full_name: "قنواتی محمدی شهاب", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_37", row_number: 37, full_name: "کاشی ساز میلاد", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_38", row_number: 38, full_name: "کرمی سیدبنیامین", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_39", row_number: 39, full_name: "گزنی محمدسجاد", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_40", row_number: 40, full_name: "لامی نژاد امیرعباس", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_41", row_number: 41, full_name: "محفوظیان نژاد سیدمحمدعلی", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_42", row_number: 42, full_name: "محمدیان کاوه", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_43", row_number: 43, full_name: "محمودی کمک آرین", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_44", row_number: 44, full_name: "مردان عرفان", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_45", row_number: 45, full_name: "مطوری محمدحسین", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_46", row_number: 46, full_name: "ملک محمدمهدی", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_47", row_number: 47, full_name: "منصوریان عبدالله", grade_label: "هفتم - ۲", grade_color: "blue" },
    { id: "st_48", row_number: 48, full_name: "منظری امیرحسین", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_49", row_number: 49, full_name: "مهرجو پارسا", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_50", row_number: 50, full_name: "وفائیان امیرمحمد", grade_label: "نهم - توکل", grade_color: "purple" },
    { id: "st_51", row_number: 51, full_name: "یاسین زاده ماهان", grade_label: "نهم - توکل", grade_color: "purple" }
];

// js/store.js

// ... (دیتای قبلی) ...

export const exerciseStudentsData = [
        {
            id: "st_1", name: "اسکندری امیرحسین", avatar: "https://ui-avatars.com/api/?name=Amirhossein+Eskandari&background=random",
            needs_exercise: true, reason: "ضعف در درک مطلب", urgency: "medium"
        },
        {
            id: "st_2", name: "آلبوعطوی امیرحسین", avatar: "https://ui-avatars.com/api/?name=Amirhossein+Albuatavi&background=random",
            needs_exercise: true, reason: "ضعف در واژگان", urgency: "high"
        },
        {
            id: "st_3", name: "انصاری محمدحسین", avatar: "https://ui-avatars.com/api/?name=Mohammadhossein+Ansari&background=random",
            needs_exercise: true, reason: "ضعف در گرامر", urgency: "medium"
        },
        {
            id: "st_4", name: "بدوی شهاب", avatar: "https://ui-avatars.com/api/?name=Shahab+Badavi&background=random",
            needs_exercise: true, reason: "عدم تحویل تمرین های خانگی", urgency: "high"
        },
        {
            id: "st_5", name: "بنی هاشمی سیدمحمد مهدی", avatar: "https://ui-avatars.com/api/?name=Seyed+Mohammad+Mahdi+Banihashemi&background=random",
            needs_exercise: true, reason: "غیبت در امتحان تعیین سطح", urgency: "high"
        },
        {
            id: "st_6", name: "بهبهانی امیرحسین", avatar: "https://ui-avatars.com/api/?name=Amirhossein+Behbahani&background=random",
            needs_exercise: true, reason: "نیاز به تمرین بیشتر", urgency: "medium"
        },
        {
            id: "st_7", name: "پاک نیت طاها", avatar: "https://ui-avatars.com/api/?name=Taha+Pakniyat&background=random",
            needs_exercise: true, reason: "ضعف در درک مطلب", urgency: "low"
        },
        {
            id: "st_8", name: "پولک کش علیرضا", avatar: "https://ui-avatars.com/api/?name=Alireza+Polakkesh&background=random",
            needs_exercise: true, reason: "ضعف در واژگان", urgency: "medium"
        },
        {
            id: "st_9", name: "حردانی ایلیا", avatar: "https://ui-avatars.com/api/?name=Ilya+Hardani&background=random",
            needs_exercise: false, reason: "", urgency: "low"
        },
        {
            id: "st_10", name: "حسینی محمدجواد", avatar: "https://ui-avatars.com/api/?name=Mohammadjavad+Hosseini&background=random",
            needs_exercise: true, reason: "ضعف در گرامر", urgency: "high"
        },
        {
            id: "st_11", name: "حیدری محمدمتین", avatar: "https://ui-avatars.com/api/?name=Mohammadmatin+Heidari&background=random",
            needs_exercise: true, reason: "عدم تحویل تمرین های خانگی", urgency: "medium"
        },
        {
            id: "st_12", name: "خیام زاده سواری نژاد مهدی", avatar: "https://ui-avatars.com/api/?name=Mahdi+Khayamzadeh&background=random",
            needs_exercise: true, reason: "غیبت در امتحان تعیین سطح", urgency: "high"
        },
        {
            id: "st_13", name: "دوستانی فر علی", avatar: "https://ui-avatars.com/api/?name=Ali+Doostanifar&background=random",
            needs_exercise: false, reason: "", urgency: "low"
        },
        {
            id: "st_14", name: "سپهری صدرا", avatar: "https://ui-avatars.com/api/?name=Sadra+Sepehri&background=random",
            needs_exercise: true, reason: "نیاز به تمرین بیشتر", urgency: "medium"
        },
        {
            id: "st_15", name: "شجاع حسین", avatar: "https://ui-avatars.com/api/?name=Hossein+Shoja&background=random",
            needs_exercise: true, reason: "ضعف در درک مطلب", urgency: "low"
        },
        {
            id: "st_16", name: "صادقی پاک حسین", avatar: "https://ui-avatars.com/api/?name=Hossein+Sadeghi+Pak&background=random",
            needs_exercise: true, reason: "ضعف در واژگان", urgency: "high"
        },
        {
            id: "st_17", name: "صالحی محمد", avatar: "https://ui-avatars.com/api/?name=Mohammad+Salehi&background=random",
            needs_exercise: false, reason: "", urgency: "low"
        },
        {
            id: "st_18", name: "طاهری نیا حسین", avatar: "https://ui-avatars.com/api/?name=Hossein+Taherinia&background=random",
            needs_exercise: true, reason: "ضعف در گرامر", urgency: "medium"
        },
        {
            id: "st_19", name: "عچرش محمدرضا", avatar: "https://ui-avatars.com/api/?name=Mohammadreza+Acharash&background=random",
            needs_exercise: true, reason: "عدم تحویل تمرین های خانگی", urgency: "medium"
        },
        {
            id: "st_20", name: "قریشوندی ابوالفضل", avatar: "https://ui-avatars.com/api/?name=Abolfazl+Ghoreishvandi&background=random",
            needs_exercise: true, reason: "غیبت در امتحان تعیین سطح", urgency: "high"
        },
        {
            id: "st_21", name: "کرمی سیدبنیامین", avatar: "https://ui-avatars.com/api/?name=Seyed+Benyamin+Karami&background=random",
            needs_exercise: false, reason: "", urgency: "low"
        },
        {
            id: "st_22", name: "مردان عرفان", avatar: "https://ui-avatars.com/api/?name=Erfan+Mardan&background=random",
            needs_exercise: true, reason: "نیاز به تمرین بیشتر", urgency: "medium"
        },
        {
            id: "st_23", name: "منظری امیرحسین", avatar: "https://ui-avatars.com/api/?name=Amirhossein+Manzari&background=random",
            needs_exercise: true, reason: "ضعف در درک مطلب", urgency: "low"
        },
        {
            id: "st_24", name: "مهرجو پارسا", avatar: "https://ui-avatars.com/api/?name=Parsa+Mehrjoo&background=random",
            needs_exercise: true, reason: "ضعف در واژگان", urgency: "medium"
        },
        {
            id: "st_25", name: "وفائیان امیرمحمد", avatar: "https://ui-avatars.com/api/?name=Amirmohammad+Vafaeian&background=random",
            needs_exercise: false, reason: "", urgency: "low"
        },
        {
            id: "st_26", name: "یاسین زاده ماهان", avatar: "https://ui-avatars.com/api/?name=Mahan+Yasinzadeh&background=random",
            needs_exercise: true, reason: "ضعف در گرامر", urgency: "high"
        }
]

// js/store.js

// ... (دیتای قبلی) ...

export const examPerformanceData = {
    exam_title: "ریاضی فصل دوم - توابع",
    stats: {
        avg: 16.4,
        max: 20,
        min: 8.5,
        count: 25,
        validity: "استاندارد",
        discrimination_index: 0.75
    },
    // توزیع نمرات برای نمودار (تعداد دانش‌آموز در هر بازه)
    distribution: [
        { label: "۰-۱۰", count: 2, height: "10%" },
        { label: "۱۰-۱۵", count: 8, height: "40%" }, // بیشترین تراکم
        { label: "۱۵-۱۸", count: 10, height: "60%" },
        { label: "۱۸-۲۰", count: 5, height: "25%" }
    ],
    students: [
        { id: 1, name: "سارا محمدی", score: 20, rank: 1, status: "A" },
        { id: 2, name: "علی رضایی", score: 18.5, rank: 2, status: "A" },
        { id: 3, name: "نیما کاظمی", score: 16, rank: 3, status: "B" },
        { id: 4, name: "کیارش رستمی", score: 14, rank: 4, status: "B" },
        { id: 5, name: "حسین حسینی", score: 9, rank: 5, status: "C" }
    ],
    questions: [
        { num: 1, text: "دامنه تابع رادیکالی زیر را بیابید...", correct_rate: "80%" },
        { num: 2, text: "کدام یک از روابط زیر تابع است؟", correct_rate: "95%" },
        { num: 3, text: "مقدار حد تابع در نقطه x=2...", correct_rate: "45%" } // سوال سخت
    ]
};


// js/store.js

// ... (دیتای قبلی) ...

export const teacherClasses = [
    { id: "c1", name: "نهم توکل" },
    { id: "c2", name: "هفتم ۲" }
];

export const mockNotes = [
    {
        id: 1,
        type: "class",
        target_name: "نهم توکل",
        text: "سطح انرژی کلاس امروز پایین بود. نیاز به استراحت بیشتر بین مباحث دارند.",
        date: "۱۴۰۴/۰۹/۲۵",
        tags: ["عمومی", "رفتاری"]
    },
    {
        id: 2,
        type: "student",
        target_name: "امیرحسین بهبهانی",
        avatar: "https://ui-avatars.com/api/?name=Ali+Rezaei&background=random",
        text: "پیشرفت عالی در حل تمرینات گرامر. تشویق شد.",
        date: "۱۴۰۴/۰۹/۳۰",
        tags: ["شخصی", "تحصیلی"]
    }
];