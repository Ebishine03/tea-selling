from django.shortcuts import redirect, get_object_or_404, render
from .models import Cart, CartItem, Product, ComboProduct, Address, Payment, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from itertools import islice
from django.template.loader import render_to_string
from django.http import JsonResponse
from .constants import  PAYMENT_METHOD_CHOICES

def chunked(iterable, size):
    it = iter(iterable)
    return iter(lambda: list(islice(it, size)), [])

@login_required
def list_products(request, category_slug):
    search_query = request.GET.get('search-query', '')
    sort_by = request.GET.get('sort-by', 'default')

    # Filter products based on category_slug
    if category_slug == 'TEA':
        products = Product.objects.filter(category='TEA')
    elif category_slug == 'SPICE':
        products = Product.objects.filter(category='SPICE')
    elif category_slug == 'combo':
        products = ComboProduct.objects.all()
    elif category_slug == 'offer':
        products = Product.objects.filter(is_offer=True)
    else:
        products = []  # Empty list for invalid types

    # Apply search query if provided
    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Apply sorting if selected
    if sort_by == 'price-low-high':
        products = products.order_by('price')
    elif sort_by == 'price-high-low':
        products = products.order_by('-price')
    elif sort_by == 'rating-high-low':
        products = products.order_by('-rating')  # Assuming you have a 'rating' field
    elif sort_by == 'date-newest':
        products = products.order_by('-created_at')  # Assuming a 'created_at' field
    elif sort_by == 'date-oldest':
        products = products.order_by('created_at')
    elif sort_by == 'name-asc':
        products = products.order_by('title')
    elif sort_by == 'name-desc':
        products = products.order_by('-title')

    # Convert queryset to a list for chunking
    product_list = list(products)
    chunked_products = list(chunked(product_list, 3))

    # Handle AJAX request for live search and sorting
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('partials/partial_product.html', {'chunked_products': chunked_products})
        return JsonResponse({'html': html})

    # If not AJAX, render the full page
    context = {
        'chunked_products': chunked_products,
        'selected_category_slug': category_slug,
    }
    return render(request, 'products/view-products.html', context)

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # Get or create the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if the product is already in the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            # If the product is already in the cart, increase the quantity
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, f"Increased quantity for {product.title}.")
            else:
                messages.error(request, f"Cannot add more {product.title}. Only {product.stock} left in stock.")
        else:
            # New cart item
            if product.stock >= 1:
                cart_item.quantity = 1
                cart_item.save()
                messages.success(request, f"Added {product.title} to your cart.")
            else:
                messages.error(request, f"Sorry, {product.title} is out of stock.")
                cart_item.delete()
        
        # Recalculate the total price of the cart
        cart.calculate_total()
        return redirect('view_cart')  # Redirect to the cart page after adding the product
    return redirect('product_list')  # Redirect if not a POST request (e.g., via GET)

@login_required
def view_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        item_id = request.POST.get('item_id')
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        if action == 'increase':
            if cart_item.quantity < cart_item.product.stock:
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, f"Increased quantity for {cart_item.product.title}.")
            else:
                messages.error(request, f"Cannot add more {cart_item.product.title}. Only {cart_item.product.stock} left in stock.")
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                messages.success(request, f"Decreased quantity for {cart_item.product.title}.")
            else:
                cart_item.delete()
                messages.success(request, f"Removed {cart_item.product.title} from your cart.")
        elif action == 'remove':
            cart_item.delete()
            messages.success(request, f"Removed {cart_item.product.title} from your cart.")

        # Recalculate the total price of the cart
        cart.calculate_total()
        return redirect('view_cart')  # Refresh the cart view after action

    context = {
        'cart_items': cart_items,
    }
    return render(request, 'products/view_cart.html', context)

@login_required
def remove_from_cart(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    cart_item.delete()
    messages.success(request, f"Removed {cart_item.product.title} from your cart.")
    cart.calculate_total()
    return redirect('view_cart')  # Redirect to the view cart page

@login_required
def clear_cart(request):
    if request.method == 'GET':
        # Clear all items from the user's cart
        CartItem.objects.filter(cart__user=request.user).delete()
        cart = get_object_or_404(Cart, user=request.user)
        cart.calculate_total()
        messages.success(request, "Cleared all items from your cart.")
        return redirect('view_cart')
    return redirect('view_cart')  # Redirect if not GET


@login_required
def buy_now(request, product_slug):
    """
    Handles the 'Buy Now' process for a single product.
    """
    product = get_object_or_404(Product, slug=product_slug)  # Get product by slug

    # Check if the product is in stock
    if not product.is_in_stock():
        messages.error(request, f"Sorry, {product.title} is out of stock.")
        return redirect('list_products', category_slug=product.category)

    if request.method == 'POST':
        # Retrieve selected address and payment method from the form
        address_id = request.POST.get('address')
        payment_method = request.POST.get('payment_method')

        if not address_id or not payment_method:
            messages.error(request, "Please select a shipping address and payment method.")
            return redirect('buy_now', product_slug=product_slug)

        address = get_object_or_404(Address, id=address_id, user=request.user)

        # Create a Payment record
        payment = Payment.objects.create(
            user=request.user,
            address=address,
            amount=product.price,
            payment_method=payment_method,
            is_completed=True,  # Set based on actual payment processing
            status='Completed',  # Adjust as per payment gateway response
        )

        # Create an Order
        order = Order.objects.create(
            user=request.user,
            payment=payment,
            shipping_address=address,
            total_price=product.price,
            status='Pending',  # Initial status; can be updated based on business logic
        )

        # Create an OrderItem and reduce stock
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            price=product.price,  # Price at purchase time
        )

        # Reduce the product stock
        product.reduce_stock(1)

        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_confirmation', order_id=order.id)

    # For GET requests, render the Buy Now checkout page
    addresses = request.user.addresses.all()
    payment_methods = PAYMENT_METHOD_CHOICES

    context = {
        'product': product,
        'addresses': addresses,
        'payment_methods': payment_methods,
    }
    return render(request, 'products/checkout.html', context)
