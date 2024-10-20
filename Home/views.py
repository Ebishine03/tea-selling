from django.shortcuts import render,redirect,get_object_or_404
from Products.models import Product,ComboProduct,Address,Category,Order
from django.contrib.auth import authenticate, login,logout
from .forms import LoginForm,ProductForm
from django.contrib import messages
from .forms import CustomUserRegistrationForm  
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from  .models import CustomUser  
from .decorators import employee_required
from .forms import ProductForm,OrderStatusForm,CustomerForm
from django.utils import timezone
from django.db.models import Q
from .models import CustomUser

from django.urls import reverse
# Create your views here.

def index(request):
    # Fetch categories by the correct slug (in lowercase)
       # Fetch categories by the correct slug (in lowercase)
    tea_category = get_object_or_404(Category, slug='tea')
    spice_category = get_object_or_404(Category, slug='spice')


    # Get recent products filtered by category
    recent_tea = Product.objects.filter(category=tea_category).order_by('-created_at')[:3]
    recent_spice = Product.objects.filter(category=spice_category).order_by('-created_at')[:3]
    recent_offer = Product.objects.filter(is_offer=True).order_by('-created_at')[:3]
    recent_combo = ComboProduct.objects.order_by('-created_at')[:3]

    # Debugging prints
    print(tea_category)
    print("Recent Combo Products:", recent_combo)
    print("Recent Offer Products:", recent_offer)
    print("Recent Spice Products:", recent_spice)
    print("Recent Tea Products:", recent_tea)

    # Context to pass to the template
    context = {
        'recent_tea': recent_tea,
        'recent_spice': recent_spice,
        'recent_offer': recent_offer,
        'recent_combo': recent_combo,
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


    return render(request,'sign_in_up.html')
@login_required


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
                # Role-Based Redirection
                if user.is_staff:
                    return redirect('employee_dashboard')  # Redirect to employee dashboard
                else:
                    return redirect('home')  # Redirect to customer home page
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'base/login.html', {'form': form})
@login_required  

  
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
            street = request.POST.get("street")
            city = request.POST.get("city")
            state = request.POST.get("state")
            pin_code = request.POST.get("pin_code")  # Updated to match the form field
            country = request.POST.get("country")

            # Log values for debugging
            print(f"Street: {street}, City: {city}, State: {state}, Pin Code: {pin_code}, Country: {country}")

            if not all([street, city, state, pin_code, country]):
                messages.error(request, "All address fields are required.")
            else:
                Address.objects.create(user=user, street=street, city=city, state=state, pin_code=pin_code, country=country)
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

def product_list(request):
    """
    Display a list of all products with optional search and category filtering.
    Supports sorting by title, price, and date, along with live search and category filtering.
    """
    search_query = request.GET.get('q', '')  # Search term (live search)
    category_id = request.GET.get('category', '')  # Selected category ID
    sort_by = request.GET.get('sort_by', '')  # Sorting criteria (A-Z, Z-A, price, etc.)

    # Fetch all products
    products = Product.objects.all()

    # Apply search query (if present)
    if search_query:
        products = products.filter(title__icontains=search_query)

    # Apply category filter (if selected)
    if category_id:
        products = products.filter(category__id=category_id)

    # Sorting options
    if sort_by == 'az':  # A-Z sort
        products = products.order_by('title')
    elif sort_by == 'za':  # Z-A sort
        products = products.order_by('-title')
    elif sort_by == 'price_asc':  # Price Low to High
        products = products.order_by('price')
    elif sort_by == 'price_desc':  # Price High to Low
        products = products.order_by('-price')
    elif sort_by == 'date_asc':  # Date Oldest First
        products = products.order_by('created_at')
    elif sort_by == 'date_desc':  # Date Newest First
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-updated_at')  # Default sort by latest update

    # Fetch all categories for filtering
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_sort': sort_by,
    }

    return render(request, 'employee/inventory_emp.html', context)

@employee_required
def add_product(request):
    """
    Allow employees to add a new product.
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.edited_by = request.user  # Track who edited
            product.save()
            form.save_m2m()  # If there are ManyToMany fields
            messages.success(request, 'Product added successfully.')
            return redirect('employee_dashboard')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Add New Product',
    }
    return render(request, 'products/add_products.html', context)

@employee_required
def edit_product(request, pk):
    """
    Allow employees to edit an existing product.
    """
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.edited_by = request.user  # Track who edited
            product.save()
            form.save_m2m()
            messages.success(request, 'Product updated successfully.')
            return redirect('employee_dashboard')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'title': 'Edit Product',
    }
    return render(request, 'products/edit_products.html', context)
@employee_required

def delete_product(request, pk):
    """
    Allow employees to delete a product.
    """
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('product_list')
    
    context = {
        'product': product,
        'title': 'Delete Product',
    }
    return render(request, 'employee/product_confirm_delete.html', context)
def customer_list(request):
    """
    Display a list of all customers with optional search.
    """
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
    """
    Display detailed information about a specific customer.
    """
    customer = get_object_or_404(CustomUser, pk=pk)
    orders = customer.orders.all().order_by('-ordered_at')
    
    context = {
        'customer': customer,
        'orders': orders,
    }
    return render(request, 'customer_detail.html', context)

@employee_required
def edit_customer(request, pk):
    """
    Allow employees to edit customer information.
    """
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
def update_order(request, pk):
    """
    Allow employees to update order status and assign delivery personnel.
    """
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Order updated successfully.')
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderStatusForm(instance=order)
    
    context = {
        'form': form,
        'order': order,
        'title': 'Update Order',
    }
    return render(request, 'order_form.html', context)
# your_app/views.py

@employee_required
def dashboard(request):
    """
    Display dashboard with product listing, add product form, and edit product functionality.
    """
    # Fetching products for the list
    products = Product.objects.all().order_by('-updated_at')

    # Metrics for the dashboard
    products_count = products.count()
    customers_count = CustomUser.objects.count()
    today = timezone.now().date()
    today_orders_count = Order.objects.filter(ordered_at__date=today).count()
    pending_orders_count = Order.objects.filter(status='pending').count()
    low_stock_products = products.filter(stock__lt=10)  # Threshold can be adjusted

    
    context = {
        'products_count': products_count,
        'customers_count': customers_count,
        'today_orders_count': today_orders_count,
        'pending_orders_count': pending_orders_count,
        'low_stock_products': low_stock_products,
        'products': products,  # List of products to display
         # Product form for adding or editing
    }

    return render(request, 'employee/inventory_emp.html', context)