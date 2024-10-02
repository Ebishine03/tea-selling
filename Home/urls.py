from django.urls import  path
from django.conf.urls.static import static
from django.conf import settings
from .views import *
urlpatterns = [
path('',index,name='home'),

path('',login_user,name='login'),

]
