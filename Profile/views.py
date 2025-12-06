import pandas as pd
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import ExelUploadForm
from .models import Student, Users
from django.views.generic import TemplateView, View
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LoginForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Student, Users


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
            national_code = str(row.get('کدملی', ''))
            user = Users.objects.create_user(
                username=national_code,
                password=national_code,
                role='student'
            )
            student = Student.objects.create(
                user=user,
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


class HomeView(TemplateView):
    template_name = 'Profile/home.html'



def student_dashboard(request):
    student = request.user.student
    return render(request, 'Profile/student_dashboard.html', {'student' : student})




class LoginView(View):
    template_name = "Profile/login.html"

    def get(self, request):
        # اگر لاگین است، مستقیم بفرستش خونه (اختیاری)
        if request.user.is_authenticated:
            return redirect("home")

        form = LoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            # فقط خود یوزر چک می‌شود
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("home")   # یا هر جایی که می‌خوای

            messages.error(request, "نام کاربری یا رمز عبور اشتباه است.")

        return render(request, self.template_name, {"form": form})


class StuedentPanelView(LoginRequiredMixin, TemplateView):
    template_name = 'Profile/student_panel.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        context['student'] = student
        return context


class LogoutView(View):
    template_name = "Profile/logout.html"
    def get(self, request):
        logout(request)
        return redirect("login")