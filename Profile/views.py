from symtable import Class

from django.shortcuts import render

import pandas as pd
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import ExelUploadForm
from .models import Student
from django.views.generic import TemplateView

class ExcelUploadView(FormView):
    template_name = 'Profile/upload_exel.html'
    form_class = ExelUploadForm
    success_url = reverse_lazy('upload_success')

    def form_valid(self, form):
        excel_file = form.cleaned_data['excel_file']
        df = pd.read_excel(excel_file)

        # تمیز کردن داده‌ها برای هر سطر
        def clean_data(value):
            if isinstance(value, str):
                # حذف هر چیزی بعد از "Name:" یا سایر بخش‌های اضافی
                cleaned_value = value.split('Name:')[0]  # حذف بعد از "Name:"
                cleaned_value = cleaned_value.strip()  # حذف فضای اضافی
                return cleaned_value
            return value  # در صورتیکه داده عددی باشد یا نوع دیگری، بدون تغییر باقی بماند

        # اعمال تمیزکاری به همه داده‌ها
        df_cleaned = df.applymap(clean_data)

        # ذخیره داده‌ها در دیتابیس
        for _, row in df_cleaned.iterrows():
            Student.objects.create(
                full_name=row.get('full_name', ''),
                fathers_name=row.get('نام پدر', ''),
                national_code=row.get('کدملی', ''),
                id_card_number=row.get('شناسنامه', ''),
                birth_date=row.get('تاریخ تولد', ''),
                birth_place=row.get('محل صدور', ''),
                sex=row.get('جنسیت', ''),
                clas=row.get('کلاس', ''),
                address=row.get('آدرس', ''),
                phone_number=row.get('همراه', ''),
                home_phone_number=row.get('ثابت', ''),
                transition=row.get('انتقالی', ''),
                description=row.get('توضیحات', ''),
            )

        return HttpResponse("داده‌ها با موفقیت وارد شدند!")

class SuccessView(TemplateView):
    template_name = 'Profile/success.html'