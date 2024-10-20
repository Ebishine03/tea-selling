from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import RegexValidator


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
    ('Completed', 'Completed'),
    ('Cancelled', 'Cancelled'),
)


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
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            # Ensure slug is unique across both categories and products
            while Product.objects.filter(slug=slug).exists() or Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    )
    
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use CustomUser instead of Customer
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    products = models.ManyToManyField(
        Product, 
        through='OrderItem', 
        related_name='orders'
    )
    total_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    ordered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_delivery = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='deliveries'
    )  # Assuming delivery personnel are users with role 'staff' or 'admin'
    
    def __str__(self):
        return f"Order #{self.id} by {self.customer.email}"
    
    def calculate_total_price(self):
        """
        Calculates and updates the total price of the order based on associated OrderItems.
        """
        total = sum(item.product.price * item.quantity for item in self.order_items.all())
        self.total_price = total
        self.save()

class OrderItem(models.Model):
    """
    Represents the relationship between an Order and a Product, including quantity and price at the time of order.
    """
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='order_items'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[
            RegexValidator(
                regex=r'^[1-9]\d*$',
                message="Quantity must be a positive integer."
            )
        ]
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2
    )  # Price at the time of order
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity} (Order #{self.order.id})"
    
    def save(self, *args, **kwargs):
        """
        Override save method to automatically set the price based on the product's current price if not set.
        """
        if not self.price and self.product:
            self.price = self.product.price
        super().save(*args, **kwargs)
 
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




class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Credit Card', 'Credit Card'),
        ('PayPal', 'PayPal'),
        ('Cash On Delivery', 'Cash On Delivery'),
        ('UPI', 'UPI'),
    ]
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    payment_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id}"
