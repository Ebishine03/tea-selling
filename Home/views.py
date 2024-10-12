from django.shortcuts import render,redirect,get_object_or_404
from Products.models import Product,ComboProduct,Address
from django.contrib.auth import authenticate, login,logout
from .forms import LoginForm
from django.contrib import messages
from .forms import CustomUserRegistrationForm  
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from  .models import CustomUser  


from django.urls import reverse
# Create your views here.

def index(request):
    recent_tea = Product.objects.filter(category='TEA').order_by('-created_at')[:3]
    recent_spice = Product.objects.filter(category='SPICE').order_by('-created_at')[:3]
    recent_offer = Product.objects.filter(is_offer=True).order_by('-created_at')[:3]
    recent_combo = ComboProduct.objects.order_by('-created_at')[:3]

    # Debugging prints
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
                return redirect('home')  # Redirect to the homepage after successful login
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'base/login.html', {'form': form})
@login_required  # Ensure the user is logged in

@login_required  # Ensure the user is logged in
def profile_view(request):
    user = get_object_or_404(CustomUser, id=request.user.id)
    addresses = Address.objects.filter(user=user)

    if request.method == "POST":
        # Handle adding a new address
        if "add_address" in request.POST:
            street = request.POST.get("street")
            city = request.POST.get("city")
            state = request.POST.get("state")
            pin_code = request.POST.get("zip_code")
            country = request.POST.get("country")

            # Create and save the new address
            Address.objects.create(user=user, street=street, city=city, state=state, pin_code=pin_code, country=country)
            messages.success(request, "Address added successfully.")
            return redirect('profile')  # Redirect to avoid re-submission

        # Handle removing an address
        elif "remove_address" in request.POST:
            address_id = request.POST.get("address_id")
            address = get_object_or_404(Address, id=address_id, user=user)
            address.delete()
            messages.success(request, "Address removed successfully.")
            return redirect('profile')  # Redirect to avoid re-submission

    context = {
        'user': user,
        'addresses': addresses
    }
    return render(request, 'base/profile.html', context)


    # Get the address object or return a 404 error if not found
    address = get_object_or_404(Address, id=address_id)

    if request.method == "POST":
        # Check if the address belongs to the logged-in user
        if address.user == request.user:
            address.delete()  # Remove the address
            messages.success(request, "Address removed successfully.")  # Add a success message
        else:
            messages.error(request, "You are not allowed to remove this address.")  # Add an error message

        return redirect('profile')  # Redirect to the profile page