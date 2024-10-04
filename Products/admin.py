from django.contrib import admin
from .models import Product, ComboProduct

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'discounted_price', 'category', 'stock', 'is_offer', 'is_latest', 'created_at')
    list_filter = ('category', 'is_offer', 'is_latest')
    search_fields = ('title', 'description')

@admin.register(ComboProduct)
class ComboProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'combo_price', 'is_offer', 'is_latest')
    list_filter = ('is_offer', 'is_latest')
    search_fields = ('name',)
    filter_horizontal = ('products',)  # Allows easier selection of multiple products for the combo
