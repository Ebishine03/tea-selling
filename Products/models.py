from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import timedelta




PAYMENT_METHOD_CHOICES = [
    ('Credit Card', 'Credit Card'),
    ('PayPal', 'PayPal'),
    ('Cash On Delivery', 'Cash On Delivery'),
    ('UPI', 'UPI'),
]
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            # Ensure slug is unique across both categories and products
            while Category.objects.filter(slug=slug).exists() or Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

class Product(models.Model):
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='products'
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_offer=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='products_created', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='products_updated', on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2
    )
    stock = models.PositiveIntegerField()
    product_image = models.ImageField(
        upload_to='product_images/', 
        blank=True, 
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    def reduce_stock(self, quantity):
        """
        Reduces the stock of the product by the given quantity.
        """
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
        else:
            raise ValueError("Not enough stock available.")
    
    def save(self, *args, **kwargs):
        # Only set the slug if it's not already set
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            
            # Ensure slug is unique within the Product model
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug

        super().save(*args, **kwargs)

    def title_has_changed(self):
        """Check if the title has changed since the last save."""
        if self.pk:  # Ensure the product has been saved
            original = Product.objects.get(pk=self.pk)
            return original.title != self.title
        return False
@property
def title_has_changed(self):
    # Check if the title has changed by comparing the current title to the original
    return self.pk and Product.objects.get(pk=self.pk).title != self.title




class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    delivery = models.ForeignKey('Delivery', on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    shipping_charge= models.DecimalField(max_digits=10, decimal_places=2,default=0)
    order_date = models.DateTimeField(auto_now_add=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
      
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    def get_delivery_charge(self):
        from .utils import calculate_delivery_charge
        return calculate_delivery_charge(self)
    
    def can_be_canceled(self):
        cancelable_time = timedelta(hours=10)  # 10-hour window
        time_diff = timezone.now() - self.order_date

        if self.status == 'cancelled':
           return False, "This order has already been cancelled."
        elif self.status == 'delivered':
           return False, "Delivered."
        elif time_diff <= cancelable_time:
            remaining_time = cancelable_time - time_diff
            hours_left = int(remaining_time.total_seconds() // 3600)
            return True, f"You can cancel this order. Time remaining: {hours_left} hours left."
        else:
          return False, "You cannot cancel this order as more than 10 hours have passed."
    def time_diff_in_hours(self):
        time_diff = timezone.now() - self.order_date
        return time_diff.total_seconds() // 3600  # Returns time in hours

    def __str__(self):
        return f"Order {self.id} - {self.customer.email}"
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)

    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of order

    def __str__(self):
        return f"{self.product.title} (x{self.quantity})"
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

    def check_stock_availability(self):
        unavailable_products = [product.title for product in self.products.all() if not product.is_in_stock()]
        return unavailable_products

    def is_all_in_stock(self):
        return all(product.is_in_stock() for product in self.products.all())
class Delivery(models.Model):
    order = models.OneToOneField(Order, related_name="delivery_info", on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    delivery_status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('dispatched', 'Dispatched'),
            ('in_transit', 'In Transit'),
            ('delivered', 'Delivered'),
            ('returned', 'Returned'),
        ],
        default='pending'
    )
    delivery_date = models.DateTimeField(null=True, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} - {self.street}, {self.city}, {self.state}, {self.pin_code}, {self.country}"

    @staticmethod
    def get_delivery_addresses(user):
        return Delivery.objects.filter(order__customer=user)
class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.pin_code}, {self.country}"
    
    @staticmethod
    def get_user_addresses(user):
        return Address.objects.filter(user=user)

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Cart of {self.user.email}"

    def calculate_total(self):
        self.total_price = sum(item.product.price * item.quantity for item in self.items.all())
        self.save()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.title} in {self.cart.user.email}'s cart"

    def increase_quantity(self, amount=1):
        if self.quantity + amount <= self.product.stock:
            self.quantity += amount
            self.save()
        else:
            raise ValueError("Cannot exceed available stock.")

    def decrease_quantity(self, amount=1):
        if self.quantity > amount:
            self.quantity -= amount
            self.save()
        else:
            self.delete()

    def get_total_price(self):
        return self.product.price * self.quantity

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('not_paid', 'Not Paid'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ], default='not_paid')
    payment_method = models.CharField(max_length=50, choices=[
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ])

    def __str__(self):
        return f"Payment for Order {self.order.id} - {self.status}"
