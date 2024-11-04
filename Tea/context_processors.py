# context_processors.py
def add_user_role(request):
    print("Context processor is loading")  # Check if this message appears
    user_role = None
    if request.user.is_authenticated:
        user_role = request.user.role
        print(user_role)
    return {'user_role': user_role, 'test_variable': "Loaded"}
