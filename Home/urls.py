from django.urls import  path
from django.conf.urls.static import static
from django.conf import settings
from .views import *
urlpatterns = [
path('',index,name='home'),
path('profile/', profile_view, name='profile'),
path('search/', search_products_home, name='search_products'),
path('login/', custom_login_view, name='login'),
path('logout/',custom_logout,name='logout'),
path('register/', register, name='register'),


]
