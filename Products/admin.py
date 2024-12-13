from django.contrib import admin
from .models import Product, ComboProduct,Address, Cart, CartItem, Payment,Review,Offer,ProductVariant

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'stock', 'created_at',)
    readonly_fields = ('linked_offers',)  # Display it in the detail view as read-only

    # Optional: Customize the fields shown in the admin detail vie
    list_filter = ('category' ,'title')
    search_fields = ('title', 'description')

@admin.register(ComboProduct)
class ComboProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price','updated_at','created_at', 'is_offer','image','description')
    list_filter = ('is_offer', 'title')
    search_fields = ('title',)
    filter_horizontal = ('products',)  
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'rating', 'created_at')
    search_fields = ('product__title', 'customer__email')
@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ( 'is_active','discount_percentage','offer_title')
    search_fields = ('product__title', 'customer__email')

admin.site.register(Address)
admin.site.register(Cart)

admin.site.register(CartItem)
admin.site.register(Payment)
admin.site.register(ProductVariant)