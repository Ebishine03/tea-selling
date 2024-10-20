from django.contrib.auth.decorators import user_passes_test

def employee_required(function=None, redirect_field_name='login', login_url='login'):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and (u.is_staff or u.role in ['admin', 'staff']),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
