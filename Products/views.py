from django.shortcuts import render
from .models import Product,ComboProduct 
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required




# Create your views 



# def view_products(request, category):
   
#     products = Product.objects.filter(category=category.upper())

#     # Apply additional filtering and sorting if required
 
#     filter_price = request.GET.get('filter-price', 'All')  # Default to 'All'
#     sort_by = request.GET.get('sort-by', 'default')  # Default to 'default'
#     search_query = request.GET.get('search-query')
#     if search_query:
#         products = products.filter(title__icontains=search_query)

#     # Apply price filtering
#     if filter_price:
#         if filter_price == '200-300':
#             products = products.filter(price__gte=200, price__lte=300)
#         elif filter_price == '300-500':
#             products = products.filter(price__gte=300, price__lte=500)
#         elif filter_price == '500-600':
#             products = products.filter(price__gte=500, price__lte=600)
#         elif filter_price == 'above-600':
#             products = products.filter(price__gte=600)
        

#     # Apply sorting logic
#     if sort_by == 'price-low-high':
#         products = products.order_by('price')
#     elif sort_by == 'price-high-low':
#         products = products.order_by('-price')
#     elif sort_by == 'rating-high-low':
#         products = products.order_by('-rating')
#     elif sort_by == 'date-newest':
#         products = products.order_by('-created_at') 
#     elif sort_by == 'date-oldest':
#         products = products.order_by('created_at')
#     elif sort_by == 'name-asc':
#         products = products.order_by('title')
#     elif sort_by == 'name-desc':
#         products = products.order_by('-title')
#     if request.is_ajax():
#         html = render_to_string('partial_product_list.html', {'products': products})
#         return JsonResponse({'html': html})

#     context = {
#         'products': products,
#         'selected_category': category,  # Pass the category to the template
#     }

#     return render(request, 'view-products.html', context)
def view_products(request, category):
    products = Product.objects.filter(category=category.upper())

    # Apply search query if present
    search_query = request.GET.get('search-query')
    if search_query:
        products = products.filter(title__icontains=search_query)

    # Apply additional filtering if present
    filter_price = request.GET.get('filter-price', 'All')
    sort_by = request.GET.get('sort-by', 'default')

    # Apply price filtering
    if filter_price:
        if filter_price == '200-300':
            products = products.filter(price__gte=200, price__lte=300)
        elif filter_price == '300-500':
            products = products.filter(price__gte=300, price__lte=500)
        elif filter_price == '500-600':
            products = products.filter(price__gte=500, price__lte=600)
        elif filter_price == 'above-600':
            products = products.filter(price__gte=600)

    # Apply sorting logic
    if sort_by == 'price-low-high':
        products = products.order_by('price')
    elif sort_by == 'price-high-low':
        products = products.order_by('-price')
    elif sort_by == 'rating-high-low':
        products = products.order_by('-rating')
    elif sort_by == 'date-newest':
        products = products.order_by('-created_at')
    elif sort_by == 'date-oldest':
        products = products.order_by('created_at')
    elif sort_by == 'name-asc':
        products = products.order_by('title')
    elif sort_by == 'name-desc':
        products = products.order_by('-title')

    # Check if the request is AJAX using the X-Requested-With header
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('partial_product.html', {'products': products})
        return JsonResponse({'html': html})

    context = {
        'products': products,
        'selected_category': category,  # Pass the category to the template
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
