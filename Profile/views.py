from urllib.parse import uses_netloc

from django.db.models import Count, OuterRef, Prefetch, Q, Subquery
from django.db.models.functions import Coalesce
import pandas as pd
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import ExelUploadForm
from .models import Student, Users
from django.views.generic import TemplateView, View, DetailView, ListView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LoginForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Student, Users, SchoolClass, TeacherUser
from question.exam_data import get_student_analyze_by_name
from django.shortcuts import get_object_or_404
from question.mixins import TeacherRequiredMixin
from question.models import AnalysisBundle
from ai_asistant_with_sina.query_cache import cached_value
from django.utils.cache import patch_vary_headers
from django.utils.translation import get_language

class ExcelUploadView(LoginRequiredMixin,TeacherRequiredMixin ,FormView):
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
                address=row.get('آدرس', ''),
                phone_number=row.get('همراه', ''),
                home_phone_number=row.get('ثابت', ''),
                transition=row.get('انتقالی', ''),
                description=row.get('توضیحات', ''),
            )

        return redirect('upload_success')

class SuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'Profile/success.html'


class HomeView(TemplateView):
    template_name = 'Profile/home.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            response = super().get(request, *args, **kwargs)
        else:
            html = cached_value(
                'guest-home-html', (request.get_host(), request.is_secure(), get_language()),
                (), 300, lambda: self._render_guest_html(request, *args, **kwargs),
            )
            # Store only the body, so middleware and cookies remain request-specific.
            response = HttpResponse(html)
        patch_vary_headers(response, ['Cookie'])
        return response

    def _render_guest_html(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs).render().content



class LoginView(View):
    template_name = "Profile/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")

        form = LoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            selected_role = form.cleaned_data["role"]

            user = authenticate(request, username=username, password=password)

            if user is None:
                messages.error(request, "نام کاربری یا رمز عبور اشتباه است.")
                return render(request, self.template_name, {"form": form})

            # اینجا نقش کاربر را چک می‌کنیم
            if user.role != selected_role:
                messages.error(request, "نقش انتخاب‌شده با حساب شما مطابقت ندارد.")
                return render(request, self.template_name, {"form": form})

            # همه چیز درست → ورود
            login(request, user)

            # هدایت به پروفایل مناسب
            if user.role == "student":
                return redirect("student panel")

            if user.role == "teacher":
                return redirect("teacher panel")

        return render(request, self.template_name, {"form": form})


class StuedentPanelView(LoginRequiredMixin, TemplateView):
    template_name = 'Profile/student_panel.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        full_name = student.full_name
        student_analyze = get_student_analyze_by_name(full_name)
        context['student'] = student
        context['student_analyze'] = student_analyze
        return context


class TeacherPanelView(LoginRequiredMixin, TemplateView):
    template_name = 'Profile/teacher_panel.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check that the teacher profile still exists before serving its cache.
        TeacherUser.objects.values('pk').get(user_id=self.request.user.pk)
        context.update(cached_value(
            'teacher-dashboard', (self.request.user.pk,),
            ('people', 'exams', 'bundles'), 60, self._load_dashboard_data,
        ))
        return context

    def _load_dashboard_data(self):

        class_counts = (
            SchoolClass.objects.filter(teacher_id=OuterRef("pk"))
            .order_by().values("teacher_id").annotate(total=Count("pk")).values("total")
        )
        student_counts = (
            TeacherUser.students.through.objects.filter(teacheruser_id=OuterRef("pk"))
            .order_by().values("teacheruser_id").annotate(total=Count("pk")).values("total")
        )
        teacher = (
            TeacherUser.objects
            .filter(user=self.request.user)
            .annotate(
                class_count=Coalesce(Subquery(class_counts), 0),
                student_count=Coalesce(Subquery(student_counts), 0),
            )
            .get()
        )

        bundle_metrics = (
            AnalysisBundle.objects
            .filter(
                teacher=self.request.user,
                status=AnalysisBundle.STATUS_SUCCESS,
            )
            .aggregate(
                analysis_count=Count(
                    'id',
                    filter=Q(stage__in=[
                        AnalysisBundle.STAGE_ONE,
                        AnalysisBundle.STAGE_TWO,
                    ]),
                ),
                exercise_plan_count=Count(
                    'id',
                    filter=Q(stage=AnalysisBundle.STAGE_THREE),
                ),
            )
        )

        return {
            'teacher': teacher,
            'class_count': teacher.class_count,
            'student_count': teacher.student_count,
            'exam_count': self.request.user.exams.count(),
            **bundle_metrics,
        }


class StudentPracticeView(LoginRequiredMixin, TemplateView):
    template_name = 'Profile/student_practice.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        full_name = student.full_name
        student_analyze = get_student_analyze_by_name(full_name)
        context['student'] = student
        context['student_analyze'] = student_analyze
        return context

class LogoutView(View):
    template_name = "Profile/logout.html"
    def get(self, request):
        logout(request)
        return redirect("login")


class StudentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Student
    template_name = 'Profile/student_detail.html'
    context_object_name = 'student'
    login_url = 'login'

    def test_func(self):
        user = self.request.user
        return (
            user.is_authenticated
            and user.role == 'teacher'
            and hasattr(user, 'teacher_profile')
        )

    def get_queryset(self):
        return self.request.user.teacher_profile.students.prefetch_related("classes")


class SchoolClassStudentView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'Profile/teacher_classes.html'

    def test_func(self):
        user = self.request.user

        return hasattr(user, 'teacher_profile') and user.role == 'teacher'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile

        classes = (
            SchoolClass.objects.filter(teacher=teacher).prefetch_related(
                Prefetch(
                    "students",
                    queryset=Student.objects.only(
                        "id", "full_name", "fathers_name", "national_code",
                    ).order_by("full_name", "pk"),
                )
            ).order_by("number", "pk")
        )
        context['teacher'] = teacher
        context['classes'] = cached_value(
            'teacher-classes', (self.request.user.pk, teacher.pk),
            ('people',), 300, lambda: list(classes),
        )
        return context


# class Techaerstudentlistview(LoginRequiredMixin ,ListView):
#     model = TeacherUser
#
#     context_object_name = 'teacher'
