from django.contrib import admin
from .models import Product, CartItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'is_out_of_stock')
    search_fields = ('name',)
    list_filter = ('stock',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'quantity', 'subtotal')
    search_fields = ('product__name', 'user__username')
