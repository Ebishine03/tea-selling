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
     path('buy-now/<slug:product_slug>/delivery_info/',delivery_info_view, name='buy_now'),
    path('buy-now/<slug:product_slug>/order-summary/',order_summary_view, name='order_summary'),
    path('buy-now/<slug:product_slug>/payment/',payment_view, name='payment'),
     path('cart/checkout/', cart_checkout_view, name='cart_checkout'),
    path('cart/payment/', payment_cart_view, name='payment_cart'),
    path('cart/delivery-info/', delivery_info_cart_view, name='delivery_info_cart'),
    

    ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)