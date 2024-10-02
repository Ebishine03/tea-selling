from django.db import models

# Create your models here.
from django.db import models

class Tea(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='teas/')

    def __str__(self):
        return self.name

class Order(models.Model):
    tea = models.ForeignKey(Tea, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return f"Order of {self.quantity} {self.tea.name}"
