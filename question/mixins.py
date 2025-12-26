from django.contrib.auth.mixins import UserPassesTestMixin

class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        if not u.is_authenticated:
            return False
        if hasattr(u, 'teacher panel') :
            return True
        return getattr(u, 'role', None) == 'teacher'