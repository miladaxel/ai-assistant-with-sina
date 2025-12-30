from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Users, Student, TeacherUser, ManagerUser, SchoolClass


admin.site.register(TeacherUser)
admin.site.register(ManagerUser)
admin.site.register(SchoolClass)
@admin.register(Users)
class CustomUserAdmin(UserAdmin):
    pass

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    search_fields = ['full_name', 'national_code']
