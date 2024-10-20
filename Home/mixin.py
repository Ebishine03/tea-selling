from django.contrib.auth.mixins import UserPassesTestMixin

class EmployeeRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.role in ['admin', 'staff'])

    def handle_no_permission(self):
        from django.shortcuts import redirect
        return redirect('login')