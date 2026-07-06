import uuid
import random
import string
from django.db import models
from django.utils import timezone

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.PositiveIntegerField(help_text="Price in BDT (৳)")
    category = models.CharField(max_length=100)
    image = models.URLField(max_length=500, default="https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&q=80&w=600")
    stock = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (Stock: {self.stock})"

    @property
    def is_out_of_stock(self):
        return self.stock <= 0

    @property
    def is_low_stock(self):
        return 0 < self.stock <= 5


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('bkash', 'bKash Wallet'),
        ('nagad', 'Nagad Wallet'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    tracking_number = models.CharField(max_length=50, unique=True, editable=False)
    guest_name = models.CharField(max_length=255)
    guest_email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    shipping_address = models.TextField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    payment_details = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    total_amount = models.PositiveIntegerField(help_text="Total in BDT (৳)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            timestamp = int(timezone.now().timestamp())
            self.tracking_number = f"ORD-{timestamp}-{random_str}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.tracking_number} - {self.guest_name} (৳{self.total_amount})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.PositiveIntegerField(help_text="Unit price in BDT at time of order")

    def __str__(self):
        return f"{self.quantity}x {self.product.name} for Order {self.order.tracking_number}"

    @property
    def item_total(self):
        return self.quantity * self.price_at_purchase
