from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Tea, Order

@admin.register(Tea)
class TeaAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('tea', 'quantity', 'name', 'email')
