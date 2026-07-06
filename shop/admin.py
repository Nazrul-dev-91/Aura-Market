from django.contrib import admin
from .models import Product, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price_at_purchase', 'item_total')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'stock', 'created_at')
    list_filter = ('category',)
    search_fields = ('name', 'category', 'description')
    list_editable = ('price', 'stock')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'guest_name', 'phone_number', 'total_amount', 'payment_method', 'payment_status', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_status', 'created_at')
    search_fields = ('tracking_number', 'guest_name', 'guest_email', 'phone_number', 'shipping_address')
    list_editable = ('status', 'payment_status')
    inlines = [OrderItemInline]
