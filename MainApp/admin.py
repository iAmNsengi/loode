from django.contrib import admin
from .models import *


class OrderAdmin(admin.ModelAdmin):
    list_display = ("client", "product", "order_date", "order_status", "ship_address")


class ClientAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "address")


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price")


class CartAdmin(admin.ModelAdmin):
    list_display = ("client", "item", "quantity", "amount")


admin.site.register(Client, ClientAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(ClientVerify)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(PasswordReset)

admin.site.site_header = "LodeShoes"
admin.site.site_title = "LodeShoes admin site"
admin.site.index_title = "LodeShoes Admin"
