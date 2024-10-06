from django.shortcuts import render

from Products.models import Product,ComboProduct
# Create your views here.




def index(request):
    
    recent_tea = Product.objects.filter(category='TEA').order_by('-created_at')[:3]
    recent_spice = Product.objects.filter(category='SPICE').order_by('-created_at')[:3]
    recent_offer = Product.objects.filter(category='OFFER').order_by('-created_at')[:3]
    recent_combo = ComboProduct.objects.all().order_by('-id')[:3]
    print(recent_combo,recent_offer,recent_spice,recent_tea)
    print('hello wohekn ')

    context = {
        'recent_tea': recent_tea,
        'recent_spice': recent_spice,
        'recent_offer': recent_offer,
        'recent_combo': recent_combo,
    }
    return render(request, 'home.html', context)


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
    return render(request, 'search_results.html', context)
