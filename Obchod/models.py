from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxLengthValidator, MinLengthValidator
class User(AbstractUser):
    # Shared fields for both Customers and Employees
    telephone = models.CharField(max_length=12, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=32, null=True, blank=True)

    # Role-based fields
    ROLE_CHOICES = [
        ('V', 'Manager'),      # Manager
        ('S', 'Product Manager'),  # Product Manager
        ('C', 'Customer')      # Customer
    ]
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, default='C')
    def is_manager(self):
        return self.role == 'V'
    def is_product_manager(self):
        return self.role == 'S' or self.role == 'V'

    def is_customer(self):
        return self.role == 'C';

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField()
    amount_left = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    def average_rating(self):
        reviews = self.review_set.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        else:
            return 0

class Order(models.Model):
    expected_delivery = models.DateTimeField()
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=32)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.CharField(max_length=32)

class OrderState(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    state = models.CharField(max_length=32)
    created_at = models.DateTimeField()

class Review(models.Model):
    review_text = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()
    price_per = models.IntegerField()
