from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from Products .models import Address
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('customer', 'Customer'),
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    
    # Additional fields for the e-commerce customer
    phone_number = models.CharField(max_length=15, blank=False)
    
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    def get_full_name(self):
    # Returns the first name, last name, or both as applicable
        return " ".join(filter(None, [self.first_name, self.last_name]))
    
  
class EmployeeProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employee_profile')
    image = models.ImageField(upload_to='employee_images/', blank=True, null=True)
    security_clearance = models.CharField(max_length=100)
    date_hired = models.DateField()
    employee_type = models.CharField(max_length=50, choices=[
        ('inventory_manager', 'Inventory Manager'),
        ('logistics_manager', 'Logistics Manager'),
        ('customer_support', 'Customer Support'),
        ('sales', 'Sales'),
        ('marketing', 'Marketing'),
    ], default='staff') 
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}'s profile"
class Notification(models.Model):
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    target_role = models.CharField(max_length=50, default='employee')  # or any default role you prefer
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Reference to the custom user model
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Notification for {self.user}: {self.message[:20]}"