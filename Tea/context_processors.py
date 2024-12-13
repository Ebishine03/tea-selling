# context_processors.pyfrom 
from Products.models import Category,Cart,CartItem
from django.db.models import Sum



def category_context(request):
    """
    Provides all active categories' name and slug for global use.
    """
    categories = Category.objects.filter(is_active=True).values('name', 'slug')
    return {'global_categories': categories}

def cart_item_count(request):
    if request.user.is_authenticated:
        total_items = CartItem.objects.filter(cart__user=request.user).aggregate(Sum('quantity'))['quantity__sum'] or 0
        return {'cart_item_count': total_items}
    return {'cart_item_count': 0}

    


def add_user_role(request):
    print("Context processor is loading")  # Check if this message appears
    user_role = None
    if request.user.is_authenticated:
        user_role = request.user.role
        print(user_role)
    return {'user_role': user_role, 'test_variable': "Loaded"}
