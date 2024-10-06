from django.db import models
from django.utils import timezone
# Define main product categories
CATEGORY_CHOICES = (
    ('TEA', 'TEA PRODUCTS'),
    ('SPICE', ' SPICE ITEMS'),
   
)

class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.FloatField()
    discounted_price = models.FloatField()
    product_image = models.ImageField(upload_to='products')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)  # Main product category
    stock = models.PositiveIntegerField(default=0)  # Remaining stock
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_offer = models.BooleanField(default=False)
    is_latest = models.BooleanField(default=True)  

    def __str__(self):
        return self.title

    def is_in_stock(self):
        return self.stock > 0



class ComboProduct(models.Model):
    title = models.CharField(max_length=200)
    products = models.ManyToManyField(Product, related_name='combos')  
    price = models.FloatField() 
    is_offer = models.BooleanField(default=False)
    image = models.ImageField(upload_to='combo_products/', blank=True, null=True)  
    description = models.TextField(blank=True, null=True)  
    created_at = models.DateTimeField(default=timezone.now)  
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
