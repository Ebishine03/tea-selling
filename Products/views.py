from decimal import Decimal
from django.shortcuts import redirect, get_object_or_404, render
from .models import Cart, CartItem, Product, ComboProduct, Address, Payment, Order, OrderItem,Category
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from itertools import islice
from django.template.loader import render_to_string
from django.http import JsonResponse,HttpResponse
from django.db import transaction
from .constants import  PAYMENT_METHOD_CHOICES
from django.utils import timezone
from .forms import DeliveryInfoForm,QuantityForm,ReviewForm
from  .models import Delivery
import uuid
def chunked(iterable, size):
    it = iter(iterable)
    return iter(lambda: list(islice(it, size)), [])
from django.db.models import Q
from django.shortcuts import render
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import JsonResponse
from .models import Product, ComboProduct, Category, Offer
from django.utils import timezone

def list_products(request, category_slug):
    search_query = request.GET.get('search-query', '')
    sort_by = request.GET.get('sort-by', 'default')

    # Dynamically fetch the category and filter products based on the category_slug
    try:
        category = Category.objects.get(slug=category_slug)  # Get the category dynamically based on slug
    except Category.DoesNotExist:
        category = None  # If category doesn't exist, return empty

    # Initialize products as an empty queryset
    products = Product.objects.none()

    # If a category is found, fetch products for that category
    if category:
        products = Product.objects.filter(category=category, is_active=True)

    # If it's combo category, fetch combo products
    if category_slug == 'combo':
        products = ComboProduct.objects.filter(is_combo=True, is_active=True)

    # If it's "offer" type, fetch products that have active offers
    if category_slug == 'offer':
        # Filter products with active offers
        products = Product.objects.filter(
            offers__is_active=True,
            offers__start_date__lte=timezone.now(),
            offers__end_date__gte=timezone.now(),
            is_active=True
        ).distinct()  # Ensure no duplicate products are returned

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
        products = products.order_by('-rating')
    elif sort_by == 'date-newest':
        products = products.order_by('-created_at')
    elif sort_by == 'date-oldest':
        products = products.order_by('created_at')
    elif sort_by == 'name-asc':
        products = products.order_by('title')
    elif sort_by == 'name-desc':
        products = products.order_by('-title')

    # Check for active offers for each product in the queryset
    for product in products:
        product.valid_offer = None  # Default value if no valid offer
        product.discounted_price = None
        if hasattr(product, 'offers'):
            # Check for an active offer
            offer = product.offers.filter(
                is_active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            ).first()
            if offer:
                product.valid_offer = offer
                for variant in product.variants.all():
                    product.discounted_price = variant.get_discounted_price(offer=offer)
                    print(product.discounted_price)

    paginator = Paginator(products, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Handle AJAX request for live search and sorting
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('partials/partial_product.html', {'page_obj': page_obj})
        return JsonResponse({'html': html})

    # If not AJAX, render the full page
    context = {
        'page_obj': page_obj,
        'selected_category_slug': category_slug,
    }
    return render(request, 'products/view-products.html', context)


@login_required
def add_to_cart(request, product_slug):
    if request.method == 'POST':
        product = get_object_or_404(Product, slug=product_slug)
        
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
    # Ensure the cart exists for the user
    cart, created = Cart.objects.get_or_create(user=request.user)
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
    # Get the product based on the slug
    product = get_object_or_404(Product, slug=product_slug)
    
    # Fetch all saved addresses for the logged-in user
    saved_addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
            # Get the address selected by the user from the dropdown
        selected_address = request.POST.get('selected_address')
        print(selected_address)

        if selected_address and selected_address != "manual":
            # If the user selected an existing address
            address = get_object_or_404(Address, id=selected_address)
            
            # Store selected address and user details in the session
            request.session['delivery_info'] = {
                'full_name': request.user.get_full_name(),
                'phone_number': request.user.phone_number,
                'home': address.home,
                'street': address.street,
                'city': address.city,
                'state': address.state,
                'pin_code': address.pin_code,
                'country': address.country,
               
            }
            print('fcgvhbjknlm,')
            print("Delivery Info Stored:", request.session['delivery_info']) 
            # Redirect to the order summary page after selecting the address
            return redirect('order_summary', product_slug=product_slug)

        elif selected_address == "manual":
            # If the user chose to enter a new address manually
            form = DeliveryInfoForm(request.POST)
            if form.is_valid():
                # Save the new address information in the session
                request.session['delivery_info'] = form.cleaned_data

                # Redirect to the order summary page after entering the new address
                return redirect('order_summary', product_slug=product_slug)

    # If it's a GET request, create a new form for manual entry
    form = DeliveryInfoForm()

    # Render the delivery_info page with the form and the saved addresses
    return render(request, 'orders/delivery_info.html', {
        'form': form,
        'product': product,
        'saved_addresses': saved_addresses,
    })

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
    orders= Order.objects.filter(customer=request.user).order_by('-order_date')
    print(orders)
    for order in orders:
        can_cancel, cancel_message = order.can_be_canceled()  # Get the cancel status and message
        order.can_cancel = can_cancel
        order.cancel_message = cancel_message  # Attach these values to the order object

    return render(request, 'orders/my_orders.html', {
        'orders': orders,
    })
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Check if the order status allows cancellation
    if order.status in ['pending', 'processing']:
        order.status = 'canceled'
        order.save()
        messages.success(request, "Order canceled successfully.")
    else:
        messages.error(request, f"Order cannot be canceled as it is already {order.status}.")

    return redirect('order_summary')
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.customer = request.user
            review.product = product
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()
    return render(request, 'submit_review.html', {'form': form, 'product': product})
def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    reviews = product.reviews.all()
    form = ReviewForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        review = form.save(commit=False)
        review.customer = request.user
        review.product = product
        review.save()
    return render(request, 'products/product_details.html', {'product': product, 'reviews': reviews, 'form': form})