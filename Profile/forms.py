from django import forms
from django.contrib.admin.forms import AuthenticationForm
from django.contrib.auth import authenticate
from .models import Student

class ExelUploadForm(forms.Form):
    excel_file = forms.FileField(label='Select an Excel file')

# class CustomLoginForm(forms.Form):
#     username = forms.CharField(max_length=150,required=True, label='Username')
#     password = forms.CharField(widget=forms.PasswordInput, required=True,label='Password')
#
#     def clean(self):
#         cleaned_data = super().clean()
#         username = self.cleaned_data.get('username')
#         password = self.cleaned_data.get('password')
#
#         if not username or not password:
#             raise forms.ValidationError("Both fields are required.")
#
#         return cleaned_data

# class StudentLoginForm(AuthenticationForm):
#     username = forms.CharField(max_length=150, required=True, label='Username')
#     password = forms.CharField(widget=forms.PasswordInput, required=True, label='Password')

# class LoginForm(forms.Form):
#     national_code = forms.CharField(max_length=20, required=True, label="کد ملی")
#     password = forms.CharField(widget=forms.PasswordInput, required=True, label="پسورد")
#
#     def clean(self):
#         cleaned_data = super().clean()
#         national_code = cleaned_data.get("national_code")
#         password = cleaned_data.get("password")
#
#         if national_code and password:
#             try:
#                 student = Student.objects.get(national_code=national_code)
#             except Student.DoesNotExist:
#                 raise forms.ValidationError("کد ملی یا پسورد اشتباه است.")
#             # چک کردن که آیا کاربر با این کد ملی و پسورد موجود است یا نه
#             user = authenticate(username=national_code, password=password)
#             if user is None:
#                 raise forms.ValidationError("کد ملی یا پسورد اشتباه است.")
#             cleaned_data["user"] = user
#         return cleaned_data



from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        label="نام کاربری",
        max_length=150,
        required=True,
    )
    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput,
        required=True,
    )
    ROLE_CHOICES = (
        ('student', 'دانش‌آموز'),
        ('teacher', 'معلم'),
        ('manager', 'مدیر'),
    )
    role = forms.ChoiceField(
        label="نقش کاربری",
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect,
    )