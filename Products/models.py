from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify
from django.db import IntegrityError
# Choices for product categories and order statuses
CATEGORY_CHOICES = (
    ('TEA', 'TEA PRODUCTS'),
    ('SPICE', 'SPICE ITEMS'),
)

ORDER_STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Processing', 'Processing'),
    ('Shipped', 'Shipped'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
)

PAYMENT_METHOD_CHOICES = (
    ('Credit Card', 'Credit Card'),
    ('PayPal', 'PayPal'),
    ('Cash on Delivery', 'Cash on Delivery'),
    ('UPI', 'UPI'),
)

PAYMENT_STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Completed', 'Completed'),
    ('Failed', 'Failed'),
)

class Category(models.Model):
    title = models.CharField(max_length=100, unique=True, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.title




class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.FloatField()
    discounted_price = models.FloatField()
    slug = models.SlugField(unique=True, blank=True)
    product_image = models.ImageField(upload_to='products')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)  
    is_offer = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Automatically generate slug from title
        if not self.slug:  # Only create slug if it hasn't been set
            self.slug = slugify(self.title)
            # Ensure slug is unique
            unique_slug = self.slug
            counter = 1
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{self.slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def is_in_stock(self):
        return self.stock > 0

    def reduce_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
        else:
            raise ValueError("Not enough stock available")
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


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.pin_code}, {self.country}"


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
        """Increase the quantity of the product in the cart."""
        if self.quantity + amount <= self.product.stock:
            self.quantity += amount
            self.save()
        else:
            raise ValueError("Cannot exceed available stock.")

    def decrease_quantity(self, amount=1):
        """Decrease the quantity of the product or remove it from the cart."""
        if self.quantity > amount:
            self.quantity -= amount
            self.save()
        else:
            self.delete()  # Remove the item if the quantity reaches 0 or less


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    is_completed = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)  # Reference ID from payment gateway
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Payment of {self.amount} by {self.user.email}"


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='Pending')
    refund_requested = models.BooleanField(default=False)
    refunded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.email} - Status: {self.status}"

    def request_refund(self):
        if self.status == 'Delivered' and not self.refund_requested:
            self.refund_requested = True
            self.status = 'Refunded'
            self.refunded_at = timezone.now()
            self.save()
            return True
        return False

    def cancel_order(self):
        """Cancel the order."""
        if self.status == 'Pending':
            self.status = 'Cancelled'
            self.save()
            return True
        return False


class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.PROTECT)  # Protect to prevent deletion if referenced in orders
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of purchase

    def __str__(self):
        return f"{self.quantity} x {self.product.title} for Order {self.order.id}"
