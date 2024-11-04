# yourapp/middleware.py

from django.shortcuts import redirect
from django.urls import reverse

class RoleBasedRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Simplified for debugging
        if request.user.is_authenticated and request.user.is_staff:
            # Redirect to employee dashboard if user is staff and on home page
            if request.path == reverse('home'):
                return redirect('employee_dashboard')

        return self.get_response(request)
