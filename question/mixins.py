from django.contrib.auth.mixins import UserPassesTestMixin

class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        if not u.is_authenticated:
            return False
        return getattr(u, 'role', None) == 'teacher' or hasattr(u, 'teacher_profile')
