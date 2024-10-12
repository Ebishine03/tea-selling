from django.contrib import admin
from .models import Product, ComboProduct,Address, Cart, CartItem, Payment

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'discounted_price', 'category', 'stock', 'is_offer', 'is_offer', 'created_at')
    list_filter = ('category', 'is_offer', )
    search_fields = ('title', 'description')

@admin.register(ComboProduct)
class ComboProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price','updated_at','created_at', 'is_offer','image','description')
    list_filter = ('is_offer', 'title')
    search_fields = ('title',)
    filter_horizontal = ('products',)  


admin.site.register(Address)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Payment)