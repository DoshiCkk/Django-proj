from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.conf import settings

class Client(AbstractUser):
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True)
    address = models.TextField(blank=True)
    ROLE_CHOICES = (
        ('buyer', 'Покупатель'),
        ('seller', 'Продавец'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')


class Product(models.Model):
    CATEGORY_CHOISES = [ 
        ('tshirt', 'Футболка'),
        ('hoodie', 'Худи'),
        ('chain', 'Цепочка'),
        ('phonecase', 'Чехол'),
    ]

    title = models.CharField(max_length=255, verbose_name='название')
    description = models.TextField(verbose_name='описание')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='цена')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOISES, verbose_name='категория')
    image = models.ImageField(upload_to='products/', verbose_name='картинка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='создано')
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sold_products'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_products',
        verbose_name='владелец'
    )

    def __str__(self):
        return self.title
    

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def total_price(self):
        return self.product.price*self.quantity

#Отзыыв
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    rating = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username}"

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        return self.product.price * self.quantity
    
User = get_user_model()
class Notification_Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    file = models.FileField(upload_to='notifications/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} — {self.message[:20]}"