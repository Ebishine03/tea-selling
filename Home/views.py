from django.shortcuts import render

from Products.models import Product
# Create your views here.




def index(request):
    
    recent_tea = Product.objects.filter(category='TEA').order_by('-created_at')[:3]
    recent_spice = Product.objects.filter(category='SPICE').order_by('-created_at')[:3]
    recent_offer = Product.objects.filter(category='OFFER').order_by('-created_at')[:3]
    recent_combo = Product.objects.filter(category='COMBO').order_by('-created_at')[:3]
    print(recent_combo,recent_offer,recent_spice,recent_tea)
    print('hello wohekn ')

    context = {
        'recent_tea': recent_tea,
        'recent_spice': recent_spice,
        'recent_offer': recent_offer,
        'recent_combo': recent_combo,
    }
    return render(request, 'home.html', context)
