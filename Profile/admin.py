from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Users, Student, TeacherUser, ManagerUser


admin.site.register(Student)
admin.site.register(TeacherUser)
admin.site.register(ManagerUser)
@admin.register(Users)
class CustomUserAdmin(UserAdmin):
    pass