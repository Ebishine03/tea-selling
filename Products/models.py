from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import timedelta
from decimal import Decimal
from django.utils.timezone import now



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active=models.BooleanField(default=True)
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
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='products_created',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='products_updated',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    stock = models.PositiveIntegerField()
    product_image = models.ImageField(
        upload_to='product_images/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    offers = models.ManyToManyField('Offer', related_name='products', blank=True)


    def __str__(self):
        return self.title

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 2)
        return 0

    def review_count(self):
        return self.reviews.count()

    def get_variants(self):
        """Retrieve all active variants."""
        return self.variants.filter(stock__gt=0)
    def linked_offers(self):
        return ", ".join(offer.offer_title for offer in self.offers.all())
   
    

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Offer(models.Model):
    OFFER_TYPE_CHOICES = [
        ('new_year', 'New Year Sale'),
        ('christmas', 'Christmas Sale'),
        ('black_friday', 'Black Friday'),
        ('clearance', 'Clearance Sale'),
        ('seasonal', 'Seasonal Offer'),
        ('other', 'Other'),
    ]

    offer_title = models.CharField(max_length=200)
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Discount percentage (e.g., 10.00 for 10%)"
    )
    discount_price = models.FloatField(null=True, blank=True)  # New field for discount price

    type_of_offer = models.CharField(
        max_length=50,
        choices=OFFER_TYPE_CHOICES,
        default='other',
        help_text="Select the type of offer for marketing purposes."
    )
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
   
    @property
    def is_valid(self):
        current_time = now()
        return (
            self.is_active and
            self.start_date <= current_time and
            (self.end_date is None or self.end_date >= current_time)
        )
    

    
    def __str__(self):
        return f"{self.discount_percentage}- {self.offer_title}"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    variant_name = models.CharField(max_length=255)
    weight = models.DecimalField(max_digits=10, decimal_places=2)  # weight in kilograms (or grams)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)  # price per unit weight
    base_price = models.FloatField(null=True, blank=True)  # New field to store base price

    stock = models.PositiveIntegerField()
    def calculate_base_price(self):
        """Calculate the base price as weight * price_per_kg."""
        return self.weight * self.price_per_kg

    def get_discount_price(self):
        """Calculate the discount price based on valid offers."""
        base_price = self.calculate_base_price()
        valid_offers = self.product.offers.filter(is_active=True, start_date__lte=now())
        if valid_offers.exists():
            offer = valid_offers.first()  # Assuming only one active offer is relevant
            discount_amount = (offer.discount_percentage / 100) * base_price
            return max(base_price - discount_amount, 0)  # Prevent negative price
        return None  # No valid offers

    def get_price_details(self):
        """Returns both base price and discount price."""
        return {
            "base_price": self.calculate_base_price(),
            "discount_price": self.get_discount_price(),
        }

    def __str__(self):
        return f"{self.variant_name} - {self.weight} kg"
  
PAYMENT_METHOD_CHOICES = [
    ('Credit Card', 'Credit Card'),
    ('PayPal', 'PayPal'),
    ('Cash On Delivery', 'Cash On Delivery'),
    ('UPI', 'UPI'),
]


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
    products = models.ManyToManyField(Product, related_name='combo')
    price = models.FloatField()
    is_combo=models.BooleanField(default=False)
    is_offer = models.BooleanField(default=False)
    image = models.ImageField(upload_to='combo_products/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active= is_active=models.BooleanField(default=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)

    def __str__(self):
        return self.title

    def check_stock_availability(self):
        unavailable_products = [product.title for product in self.products.all() if not product.is_in_stock()]
        return unavailable_products
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            # Ensure slug is unique within the ComboProduct model
            while ComboProduct.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)
    def is_all_in_stock(self):
        return all(product.is_in_stock() for product in self.products.all())
class Delivery(models.Model):
    order = models.OneToOneField(Order, related_name="delivery_info", on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    home=models.CharField(max_length=255,default='')
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
    home=models.CharField(max_length=255,default='')
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.home}{self.street}, {self.city}, {self.state}, {self.pin_code}, {self.country}"
    
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


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(null=True, blank=True)
    media = models.ImageField(upload_to='reviews/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)    
    is_active=models.BooleanField(default=True)
    
    
    class Meta:
        unique_together = ('product', 'customer')


    def __str__(self):
        return f"Review for {self.product.title} by {self.customer.username}"