from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

created_at = models.DateTimeField(auto_now_add=True, default=timezone.now)


class Login(models.Model):
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20)

    def __str__(self):
        return self.username


class Register(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='register_info')
    full_name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.full_name


class Cake(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    size = models.CharField(max_length=50)   # keep general for catalog
    shape = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='cake_images/')

    def __str__(self):
        return self.name


class CustomCakeRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reference_cake = models.ForeignKey(Cake, on_delete=models.SET_NULL, blank=True, null=True)
    cake_name = models.CharField(max_length=100, blank=True, null=True)

    flavor = models.CharField(max_length=50)
    shape = models.CharField(max_length=50)
    size = models.CharField(max_length=20)
    layers = models.PositiveIntegerField()
    weight = models.FloatField()
    quantity = models.PositiveIntegerField()
    toppings = models.TextField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    details = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.cake_name or 'Custom Cake'}"


class CakeReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.cake.name}"


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Ongoing', 'Ongoing'),
        ('Delivered', 'Delivered'),
        ('Rejected', 'Rejected')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ordered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.cake.name} ({self.user.username})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.cake.name} (Order #{self.order.id})"

