from decimal import Decimal
from django.shortcuts import redirect, get_object_or_404, render
from .models import Cart, CartItem, Product, ComboProduct, Address, Payment, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from itertools import islice
from django.template.loader import render_to_string
from django.http import JsonResponse,HttpResponse
from django.db import transaction
from .constants import  PAYMENT_METHOD_CHOICES
from django.utils import timezone
from .forms import DeliveryInfoForm,QuantityForm
from  .models import Delivery
import uuid
def chunked(iterable, size):
    it = iter(iterable)
    return iter(lambda: list(islice(it, size)), [])

def list_products(request, category_slug):
    search_query = request.GET.get('search-query', '')
    sort_by = request.GET.get('sort-by', 'default')

    # Filter products based on category_slug
    if category_slug == 'tea':
        products = Product.objects.filter(category__slug='tea')
    elif category_slug == 'spices':
        products = Product.objects.filter(category__slug='spices')
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
    return redirect('view_cart')  
@login_required
def clear_cart(request):
    if request.method == 'GET':
       
        CartItem.objects.filter(cart__user=request.user).delete()
        cart = get_object_or_404(Cart, user=request.user)
        cart.calculate_total()
        messages.success(request, "Cleared all items from your cart.")
        return redirect('view_cart')
    return redirect('view_cart')  


@login_required
def delivery_info_view(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    
    if request.method == 'POST':
        form = DeliveryInfoForm(request.POST)
        if form.is_valid():
            # Save delivery information temporarily in session
            request.session['delivery_info'] = form.cleaned_data
            return redirect('order_summary', product_slug=product_slug)
    else:
        form = DeliveryInfoForm()
    
    return render(request, 'orders/delivery_info.html', {'form': form, 'product': product})

@login_required
def cart_checkout_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    
    if not cart_items:
        # Redirect to a message or empty cart page
        return redirect('view_cart')  # Adjust as needed

    delivery_info = request.session.get('delivery_info')
    
    if not delivery_info:
        return redirect('delivery_info_cart')

    # Assuming a static delivery charge for simplicity; adjust as necessary
    delivery_charge = Decimal('5.00')
    total_price = sum(item.get_total_price() for item in cart_items) + delivery_charge

    if request.method == 'POST':
        # Process delivery info and confirm order
        order_details = {
            'total_price': str(total_price),
            'delivery_charge': str(delivery_charge),
        }
        request.session['order_details'] = order_details
        return redirect('payment_cart')

    return render(request, 'orders/cart_checkout.html', {
        'cart_items': cart_items,
        'delivery_info': delivery_info,
        'total_price': total_price,
        'delivery_charge': delivery_charge,
    })

@login_required
def payment_cart_view(request):
    delivery_info = request.session.get('delivery_info')
    order_details = request.session.get('order_details')

    if not order_details or not delivery_info:
        return redirect('delivery_info_cart')

    total_price = order_details['total_price']
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    if request.method == 'POST':
        # Check stock availability for all items
        for item in cart_items:
            if item.product.stock < item.quantity:
                return render(request, 'orders/payment_cart.html', {
                    'error': "Not enough stock available for one or more items."
                })

        # Deduct stock and create the order
        order = Order.objects.create(
            customer=request.user,
            total_price=total_price,
            status='pending',
            tracking_number=str(uuid.uuid4())
        )

        for item in cart_items:
            item.product.reduce_stock(item.quantity)
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        Delivery.objects.create(
            order=order,
            **delivery_info
        )

        Payment.objects.create(
            order=order,
            amount=total_price,
            payment_method='cash_on_delivery'  # This can be dynamically set
        )

        # Clear session data after order creation
        del request.session['order_details']
        del request.session['delivery_info']
        cart.items.all().delete()  # Clear the cart items after successful payment

        return render(request, 'orders/order_confirmation.html', {'order': order})

    return render(request, 'orders/payment_cart.html', {
        'total_price': total_price,
        'cart_items': cart_items,
    })

@login_required
def delivery_info_cart_view(request):
    if request.method == 'POST':
        form = DeliveryInfoForm(request.POST)
        if form.is_valid():
            # Save delivery information temporarily in session
            request.session['delivery_info'] = form.cleaned_data
            return redirect('cart_checkout')
    else:
        form = DeliveryInfoForm()

    return render(request, 'orders/delivery_info.html', {'form': form})

def order_summary_view(request, product_slug):
    # Retrieve the product and delivery information from the session
    product = get_object_or_404(Product, slug=product_slug)
    delivery_info = request.session.get('delivery_info')

    # Redirect to delivery info if delivery information is missing
    if not delivery_info:
        return redirect('buy_now', product_slug=product_slug)

    # Define a static delivery charge or calculate dynamically as needed
    delivery_charge = Decimal('5.00')

    # Handle the POST request for setting quantity and calculating total price
    if request.method == 'POST':
        quantity_form = QuantityForm(request.POST)
        if quantity_form.is_valid():
            quantity = quantity_form.cleaned_data['quantity']
            total_price = (Decimal(product.price) * Decimal(quantity)) + delivery_charge
            quantity_options = list(range(1, 11))

            # Store order details in the session
            request.session['order_details'] = {
                'product_id': product.id,
                'quantity': quantity,
                'total_price': str(total_price),  # Store as string for JSON compatibility
                'delivery_charge': str(delivery_charge),
                'quantity_options': quantity_options,
            }
            return redirect('payment', product_slug=product_slug)
    else:
        # Initial form setup for GET requests
        quantity_form = QuantityForm(initial={'quantity': 1})

    # Calculate expected delivery date and total price for initial display
    expected_delivery_date = timezone.now() + timezone.timedelta(days=5)
    default_quantity = 1
    total_price = (Decimal(product.price) * Decimal(default_quantity)) + delivery_charge

    # Render the template with all necessary data
    return render(request, 'orders/order_summary.html', {
        'product': product,
        'quantity_form': quantity_form,
        'delivery_info': delivery_info,
        'expected_delivery_date': expected_delivery_date,
        'delivery_charge': delivery_charge,
        'quantity_options': list(range(1, 11)),
        'total_price': total_price,
    })
def payment_view(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    order_details = request.session.get('order_details')
    delivery_info = request.session.get('delivery_info')

    # Check if session data exists; redirect if missing
    if not order_details or not delivery_info:
        return redirect('order_summary', product_slug=product_slug)

    total_price = order_details.get('total_price')  # Access total_price after validation
    tracking_number = str(uuid.uuid4())

    if request.method == 'POST':
        # Check stock availability
        quantity = order_details['quantity']
        if product.stock < int(quantity):
            return render(request, 'orders/payment.html', {'product': product, 'error': "Not enough stock available."})

        # Deduct stock
        product.reduce_stock(int(quantity))

        # Create Order and Delivery
        order = Order.objects.create(
            customer=request.user,
            total_price=order_details['total_price'],
            status='pending',
            tracking_number=tracking_number
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )

        Delivery.objects.create(
            order=order,
            **delivery_info
        )

        # Create Payment (default status is 'not_paid')
        Payment.objects.create(
            order=order,
            amount=order_details['total_price'],
            payment_method='cash_on_delivery'  # This can be dynamically set
        )

        # Clear session data after order creation
        request.session.pop('order_details', None)
        request.session.pop('delivery_info', None)

        print('Order Created')

        return render(request, 'orders/order_confirmation.html', {'order': order})

    return render(request, 'orders/payment.html', {'product': product, 'total_price': total_price})

def order_tracking_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)

    return render(request, 'orders/tracking_order.html', {
        'order': order,
    })
def cancel_order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)

    if request.method == 'POST':
        order.status = 'canceled'
        order.save()
        return redirect('my_orders')  # Redirect to My Orders page

    return render(request, 'orders/cancel_order.html', {
        'order': order,
    })
def my_orders_view(request):
    orders = Order.objects.filter(customer=request.user)

    return render(request, 'orders/my_orders.html', {
        'orders': orders,
    })
