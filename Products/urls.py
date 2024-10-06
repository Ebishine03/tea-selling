from django.urls import  path
from django.conf.urls.static import static
from django.conf import settings
from .views import *
urlpatterns = [
path('view-products/<str:category>/',view_products,name='view-products'),
#  path('view-products/<slug:category_slug>/', view_products, name='product-view_products'),




]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)