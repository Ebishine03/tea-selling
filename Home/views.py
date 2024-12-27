# Standard Library Imports
from collections import defaultdict
from itertools import chain, zip_longest

# Django Core Imports
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now

# App-specific Imports
from Products.models import (
    Address, 
    Category, 
    ComboProduct, 
   
    Offer, 
    Order, 
    Product,
)
from Tea.context_processors import add_user_role
from .decorators import employee_required
from .forms import *
from .models import CustomUser
from .notifications import send_notification

# Create your views here.
def group_into_chunks(iterable, chunk_size):
    """Groups an iterable into chunks of a specified size."""
    args = [iter(iterable)] * chunk_size
    return zip_longest(*args)
def index(request):
    # Fetch all categories and their products
    categories = Category.objects.prefetch_related(
        Prefetch(
            'products', 
            queryset=Product.objects.filter(is_active=True).prefetch_related('variants', 'offers')
        )
    )

    categorized_products = defaultdict(list)
    products_with_valid_offers = []

    for category in categories:
        category_products = []
        for product in category.products.all()[:3]:  # Get only the recent three products
            product_data = {
                'product': product,
                'variants': [],
                'category_name': category.name,
                'category_slug': category.slug,
            }

            for variant in product.variants.all():
                prices = variant.get_price_details()
                base_price = prices['base_price']
                discount_price = prices['discount_price']
                discount_percentage = ((base_price - discount_price) / base_price * 100) if discount_price is not None else 0

                # Check if there are valid offers
                valid_offers = [offer for offer in product.offers.all() if offer.is_valid]

                # If the product has a valid offer, append the offer details
                if valid_offers:
                    valid_offer = valid_offers[0]  # Take the first valid offer
                    products_with_valid_offers.append({
                        'product': product,
                        'variant': variant,
                        'category_name': category.name,
                        'category_slug': category.slug,
                        'offer': valid_offer,
                        'discount_price': discount_price,
                        'discount_percentage': discount_percentage,
                        'base_price': base_price,
                    })

                    # Add variant details with discount price and percentage
                    product_data['variants'].append({
                        'variant': variant,
                        'base_price': base_price,
                        'discount_price': discount_price,
                        'discount_percentage': discount_percentage,
                    })
                else:
                    # If no valid offer, only append the base price without discount info
                    product_data['variants'].append({
                        'variant': variant,
                        'base_price': base_price,
                    })

            category_products.append(product_data)
        categorized_products[category.name] = category_products

    # Ensure unique products with offers
    product_ids_with_offers = set()
    unique_products_with_valid_offers = []
    for product in products_with_valid_offers:
        if product['product'].id not in product_ids_with_offers:
            unique_products_with_valid_offers.append(product)
            product_ids_with_offers.add(product['product'].id)

    products_with_valid_offers = unique_products_with_valid_offers[:3]  # Keep only the recent three unique products with valid offers

    context = {
        'categorized_products': dict(categorized_products),
        'offer_products': products_with_valid_offers,
    }

    return render(request, 'base/home.html', context)

def search_products_home(request):
    query = request.GET.get('q', '')  # Get the search query
    if query:
        products = Product.objects.filter(title__icontains=query)  # Search by product title
    else:
        products = Product.objects.all()  # If no search query, return all products

    context = {
        'products': products,
        'search_query': query,
    }
    return render(request, 'base/search_results.html', context)



def register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  
            login(request, user)  
            messages.success(request, "Your account has been created successfully!")
            return redirect('home')  
        else:
            messages.error(request, "") 
          
    else:
        form = CustomUserRegistrationForm()
    
    return render(request, 'base/sign_in_up.html', {'form': form})

def custom_logout(request):
    logout(request)  # Log out the user
    return redirect(reverse('home'))
def custom_login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on user role
                if user.role == 'staff':
                    return redirect('employee_dashboard')  # Redirect to employee dashboard
                else:
                    return redirect('home')  # Redirect to customer home page
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'base/login.html', {'form': form})
@login_required  
    
def customer_list(request):
   
    search_query = request.GET.get('q', '')
    customers = CustomUser.objects.all().order_by('-user__date_joined')

    if search_query:
        customers = customers.filter(user__email__icontains=search_query)

    context = {
        'customers': customers,
        'search_query': search_query,
    }
    return render(request, 'customer_list.html', context)
def customer_detail(request, pk):
   
   
    customer = get_object_or_404(CustomUser, pk=pk)
    orders = customer.orders.all().order_by('-ordered_at')
    
    context = {
        'customer': customer,
        'orders': orders,
    }
    return render(request, 'customer_detail.html', context)

@employee_required
def edit_customer(request, pk):
  
    customer = get_object_or_404(CustomUser, pk=pk)
    user = customer.user
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer information updated successfully.')
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=user)
    
    context = {
        'form': form,
        'customer': customer,
        'title': 'Edit Customer',
    }
    return render(request, 'customer_form.html', context)
@employee_required
def delete_customer(request, pk):
    """
    Allow employees to delete a customer.
    """
    customer = get_object_or_404(CustomUser, pk=pk)
    user = customer.user
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Customer deleted successfully.')
        return redirect('customer_list')
    
    context = {
        'customer': customer,
        'title': 'Delete Customer',
    }
    return render(request, 'customer_confirm_delete.html', context)
@employee_required
def order_list(request):
    """
    Display a list of all orders with optional search and filtering.
    """
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    delivery_person_id = request.GET.get('delivery_person', '')
    
    orders = Order.objects.all().order_by('-ordered_at').select_related('customer__user', 'assigned_delivery')
    
    if search_query:
        orders = orders.filter(
            Q(customer__user__email__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if delivery_person_id:
        orders = orders.filter(assigned_delivery__id=delivery_person_id)
    
    delivery_personnel = CustomUser.objects.filter(is_staff=True)
    
    context = {
        'orders': orders,
        'delivery_personnel': delivery_personnel,
        'search_query': search_query,
        'status_filter': status_filter,
        'delivery_person_id': delivery_person_id,
    }
    return render(request, 'order_list.html', context)
@employee_required
def order_detail(request, pk):
    """
    Display detailed information about a specific order.
    """
    order = get_object_or_404(Order, pk=pk)
    order_items = order.order_items.all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'order_detail.html', context)


@employee_required
def dashboard_employee(request):
    add_user_role(request)

    # Fetch all products and orders for search and statistics
    all_products = Product.objects.filter(is_active=True)
    all_orders = Order.objects.all().order_by('-order_date')
 # Fetch employee-specific notifications

    # Count unread notifications
    
   

    recent_products = all_products.order_by('-created_at')[:5]
    recent_orders = all_orders[:10]
    categories = Category.objects.all()
    

    # Search parameters
    product_search_query = request.GET.get('product_search_query', '').strip()
    order_search_query = request.GET.get('order_search_query', '').strip()

    # Apply search logic if a search query is provided; otherwise, use recent products
    products = (
        all_products.filter(
            Q(title__icontains=product_search_query) | 
            Q(description__icontains=product_search_query)
        ) if product_search_query else recent_products
    )

    # Order search logic with support for multi-word names
    if order_search_query:
        name_parts = order_search_query.split()
        orders = all_orders.filter(
            Q(tracking_number__icontains=order_search_query) |
            Q(status__icontains=order_search_query) |
            (
                Q(customer__first_name__icontains=name_parts[0]) & 
                Q(customer__last_name__icontains=name_parts[1])
            ) if len(name_parts) == 2 else (
                Q(customer__first_name__icontains=order_search_query) |
                Q(customer__last_name__icontains=order_search_query)
            )
        )
    else:
        orders = recent_orders

    # Handle AJAX request for dynamic updates
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        products_html = render_to_string('partials/product_table_partial.html', {'products': products})
        orders_html = render_to_string('partials/order_partial.html', {'orders': orders})
        return JsonResponse({'products_html': products_html, 'orders_html': orders_html})

 

    # Context for the full page render
    context = {
        'products': products,
        'orders': orders,
        'categories': categories,
        'products_count': all_products.count(),
        'customers_count': CustomUser.objects.count(),
        
        'today_orders_count': all_orders.filter(order_date=timezone.now().date()).count(),
        'pending_orders_count': all_orders.filter(status='pending').count(),
        'processed_orders_count': all_orders.filter(status='processed').count(),

        'canceled_orders_count': all_orders.filter(status='canceled').count(),
         'delivered_orders_count': all_orders.filter(status='delivered').count(),
        'shipped_orders_count': all_orders.filter(status='shipped').count(),
        'total_orders':all_orders.count(),
        'low_stock_products_count': all_products.filter(stock__gt=0, stock__lt=10).count(),
        'out_of_stock_products_count': all_products.filter(stock=0).count(),
        'statuses': Order.STATUS_CHOICES,
        'product_search_query': product_search_query,
        'order_search_query': order_search_query,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count
       
    }
    
    print()
    return render(request, 'employee/inventory_emp.html', context)



@employee_required
def employee_profile(request):
    user = request.user  # Get the logged-in user

    try:
        employee_profile = EmployeeProfile.objects.get(user=user)
    except EmployeeProfile.DoesNotExist:
        employee_profile = None

    # Process form submissions
    if request.method == 'POST':
        user_form = CustomUserForm(request.POST, instance=user)
        if employee_profile:
            employee_form = EmployeeProfileForm(request.POST, request.FILES, instance=employee_profile)
        else:
            employee_form = None

        # Validate and save forms
        if user_form.is_valid() and (employee_form.is_valid() if employee_form else True):
            user_form.save()
            if employee_profile:
                employee_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('employee_dashboard')  # Redirect after successful update
    else:
        # Display forms with current data
        user_form = CustomUserForm(instance=user)
        if employee_profile:
            employee_form = EmployeeProfileForm(instance=employee_profile)
        else:
            employee_form = None

    context = {
        'user_form': user_form,
        'employee_form': employee_form,
        'employee_profile': employee_profile
    }

    return render(request, 'employee/employee_profile.html', context)


  
def profile_view(request):
    user = get_object_or_404(CustomUser, id=request.user.id)
    addresses = Address.objects.filter(user=user)

    if request.method == "POST":
        
        if "update_profile" in request.POST:
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            phone_number = request.POST.get("phone_number")

            if not all([first_name, last_name, phone_number]):
                messages.error(request, "All profile fields are required.")
            else:
                user.first_name = first_name
                user.last_name = last_name
                user.phone_number = phone_number
                user.save()
                messages.success(request, "Profile updated successfully.")
            return redirect('profile')

        elif "add_address" in request.POST:
            
            home=request.POST.get("home")
            street = request.POST.get("street")
            city = request.POST.get("city")
            state = request.POST.get("state")
            pin_code = request.POST.get("pin_code")  # Updated to match the form field
            country = request.POST.get("country")

            # Log values for debugging
            print(f" Home:{home}, Street: {street}, City: {city}, State: {state}, Pin Code: {pin_code}, Country: {country}")

            if not all([home,street, city, state, pin_code, country]):
                messages.error(request, "All address fields are required.")
            else:
                Address.objects.create(user=user,home=home, street=street, city=city, state=state, pin_code=pin_code, country=country)
                messages.success(request, "Address added successfully.")
            return redirect('profile')  

        elif "remove_address" in request.POST:
            address_id = request.POST.get("address_id")
            address = get_object_or_404(Address, id=address_id, user=user)
            address.delete()
            messages.success(request, "Address removed successfully.")
            return redirect('profile')  

    context = {
        'user': user,
        'addresses': addresses
    }
    return render(request, 'base/profile.html', context)

@employee_required

@employee_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.is_active = True
            product.save()
            form.save_m2m()
            
            # Notify relevant users (e.g., admin, inventory managers)
           
            
            messages.success(request, 'Product added successfully.')
            return redirect('employee_dashboard')
    else:
        form = ProductForm()
    
    context = {'form': form, 'title': 'Add New Product'}
    return render(request, 'products/add_products.html', context)

@employee_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.updated_by = request.user
            product.save()
            form.save_m2m()

            # Notify for product update
            
            messages.success(request, 'Product updated successfully.')
            return redirect('all_products')
    else:
        form = ProductForm(instance=product)

    context = {'form': form, 'title': 'Edit Product', 'product': product}
    return render(request, 'products/edit_products.html', context)

@employee_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product.is_active = False
        product.save()

 
        

        messages.success(request, 'Product deleted successfully.')
    return redirect('employee_dashboard')

@employee_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()

          
            messages.success(request, 'Category added successfully!')
            return redirect('employee_dashboard')
    else:
        form = CategoryForm()
    
    return render(request, 'employee/add_category.html', {'form': form})

@employee_required
def update_order_status(request):
    order_id = request.POST.get("order_id")
    status = request.POST.get("status")

    if order_id and status:
        order = get_object_or_404(Order, id=order_id)
        order.status = status
        order.save()
        

        messages.success(request, "Order status updated successfully.")
    else:
        messages.error(request, "Failed to update order status. Missing data.")
    
    return redirect('employee_dashboard')

@employee_required
def all_orders_view(request):
    search_query = request.GET.get('order_search_query', '')
    selected_status = request.GET.get('order_status', '')
    selected_category = request.GET.get('order_category', '')

    orders = Order.objects.select_related('delivery_info').all().order_by('-order_date')

    if search_query:
        orders = orders.filter(
            Q(customer__first_name__icontains=search_query) |
            Q(customer__last_name__icontains=search_query) |
            Q(tracking_number__icontains=search_query) |
            Q(delivery_info__state__icontains=search_query) |
            Q(delivery_info__city__icontains=search_query) |
            Q(delivery_info__country__icontains=search_query) |
            Q(delivery_info__pin_code__icontains=search_query)
        )

    if selected_status:
        orders = orders.filter(status=selected_status)

    if selected_category:
        orders = orders.filter(items__product__category__name=selected_category).distinct()

    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        orders_html = render_to_string('partials/order_partial.html', {'orders': orders_page})
        return JsonResponse({'orders_html': orders_html, 'has_next': orders_page.has_next()})

    categories = Category.objects.all()
    context = {'orders': orders_page, 'statuses': Order.STATUS_CHOICES, 'categories': categories, 'paginator': paginator}
    return render(request, 'employee/all_orders.html', context)

@employee_required
def all_products_view(request):
    search_query = request.GET.get('all_product_search_query', '')
    price_range = request.GET.get('price_range', '')
    sort_by = request.GET.get('sort_by', '')
    category_id = request.GET.get('category', '')

    products = Product.objects.filter(is_active=True)

    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    if price_range:
        price_ranges = {'0-50': (0, 50), '50-100': (50, 100), '100-150': (100, 150),
                        '150-200': (150, 200), '200-250': (200, 250), '250-300': (300, None)}
        min_price, max_price = price_ranges.get(price_range, (None, None))
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)

    sort_options = {'price-low-high': 'price', 'price-high-low': '-price', 'date-newest': '-created_at',
                    'date-oldest': 'created_at', 'name-asc': 'title', 'name-desc': '-title'}
    if sort_by in sort_options:
        products = products.order_by(sort_options[sort_by])

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        products_html = render_to_string('partials/product_table_partial.html', {'products': products_page})
        return JsonResponse({'products_html': products_html, 'has_next': products_page.has_next()})

    categories = Category.objects.all()
    context = {'search_query': search_query, 'sort_by': sort_by, 'products': products_page,
               'categories': categories, 'paginator': paginator}
    return render(request, 'employee/all_products.html', context)

@employee_required
def notifications_view(request):
    notifications = request.user.notifications.filter(is_read=False)
    return render(request, 'employee/notifications.html', {'notifications': notifications})

