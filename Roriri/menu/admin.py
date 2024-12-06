from django.contrib import admin
from menu.models import Order,Cart,CartItem,MenuItem


admin.site.register(Order)
admin.site.register(CartItem)
admin.site.register(Cart)
admin.site.register(MenuItem)
# Register your models here.
