from django.contrib import admin
from .models import Product, ComboProduct

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'discounted_price', 'category', 'stock', 'is_offer', 'is_latest', 'created_at')
    list_filter = ('category', 'is_offer', 'is_latest')
    search_fields = ('title', 'description')

@admin.register(ComboProduct)
class ComboProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price','updated_at','created_at', 'is_offer','image','description')
    list_filter = ('is_offer', 'title')
    search_fields = ('title',)
    filter_horizontal = ('products',)  
