from django.contrib import admin
from .models import *

admin.site.register(Product)
admin.site.register(Client)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Notification_Order)
