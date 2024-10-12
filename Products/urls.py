from django.urls import  path
from django.conf.urls.static import static
from django.conf import settings
from .views import *

urlpatterns = [
    
 path('view-products/<slug:category_slug>/', list_products, name='view-products'), 
 path('cart/', view_cart, name='view_cart'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', clear_cart, name='clear_cart'),
    path('buy-now/<slug:product_slug>/', buy_now, name='buy_now'),
    path('checkout/',buy_now,name='checkout')
    ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)