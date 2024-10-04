from django.shortcuts import render
from .models import Product,ComboProduct 

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
# from .models import Product, Cart, CartItem
from django.shortcuts import render
from .models import Product

# Create your views 

def view_products(request, category=None):
    if category:
        
        category = category.upper()
        if category == 'ALL':
            products = Product.objects.all()  
        else:
            products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()  
    
    context = {
        'products': products,
        'selected_category': category, 
    }
    return render(request, 'view-products.html', context)



def combo_products_view(request):
    combos = ComboProduct.objects.all()  # Get all combo products
    context = {'combos': combos}
    return render(request, 'view_products.html', context)

# def offer_products_view(request):
#     offers = Offer.objects.all()  # Get all offer products
#     context = {'offers': offers}
#     return render(request, 'offer_products.html', context)
# views.py



# @login_required
# def add_to_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)

#     # Get or create the cart for the user
#     cart, created = Cart.objects.get_or_create(user=request.user)

#     # Check if the product is already in the cart
#     cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

#     if not created:
#         # If it already exists, increase the quantity
#         cart_item.quantity += 1
#     cart_item.save()

#     return redirect('view-cart')  # Redirect to the cart view after adding

# @login_required
# def buy_now(request, product_id):
#     product = get_object_or_404(Product, id=product_id)

#     # You can implement your buying logic here, like creating an order

#     return redirect('checkout')  # Redirect to the checkout page
