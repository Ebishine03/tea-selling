from django.urls import  path
from django.conf.urls.static import static
from django.conf import settings
from .views import *
from  . import views
urlpatterns = [
path('',index,name='home'),
path('profile/', profile_view, name='profile'),
path('search/', search_products_home, name='search_products'),
path('login/', custom_login_view, name='login'),
path('logout/',custom_logout,name='logout'),
path('register/', register, name='register'),

  # Employee 
    path('employee/', dashboard, name='employee_dashboard'),
    path('employee/products/', views.product_list, name='product_list'),
    path('employee/products/add/', views.add_product, name='add_product'),
    path('employee/products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('employee/products/delete/<int:pk>/', views.delete_product, name='delete_product'),

    # Customer Management
    path('employee/customers/', views.customer_list, name='customer_list'),
    path('employee/customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('employee/customers/edit/<int:pk>/', views.edit_customer, name='edit_customer'),
    path('employee/customers/delete/<int:pk>/', views.delete_customer, name='delete_customer'),



    # Order Management
    path('employee/orders/', views.order_list, name='order_list'),
    path('employee/orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('employee/orders/<int:pk>/update/', views.update_order, name='update_order'),

]
