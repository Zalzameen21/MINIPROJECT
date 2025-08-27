from django.db import models
from django.contrib.auth.models import User

class Login(models.Model):
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20)

    def __str__(self):
        return self.username


class Register(models.Model):
    full_name = models.CharField(max_length=100)
    dob = models.DateField()
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10)
    login = models.OneToOneField(Login, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.full_name



class Cake(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    size = models.CharField(max_length=50)
    shape = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='cake_images/')

    def __str__(self):
        return self.name

class CakeReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.cake.name}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_at = models.DateTimeField(auto_now_add=True)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.cake.name} ({self.user.username})"
