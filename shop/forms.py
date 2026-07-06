from django import forms
from .models import Product, Order

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'image', 'stock']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full bg-white border border-gray-200 rounded-xl px-3 py-2 text-xs focus:ring-1 focus:ring-black focus:outline-none'}),
            'category': forms.TextInput(attrs={'class': 'w-full bg-white border border-gray-200 rounded-xl px-3 py-2 text-xs focus:ring-1 focus:ring-black focus:outline-none'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'w-full bg-white border border-gray-200 rounded-xl px-3 py-2 text-xs focus:ring-1 focus:ring-black focus:outline-none'}),
            'price': forms.NumberInput(attrs={'class': 'w-full bg-white border border-gray-200 rounded-xl px-3 py-2 text-xs focus:ring-1 focus:ring-black focus:outline-none'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full bg-white border border-gray-200 rounded-xl px-3 py-2 text-xs focus:ring-1 focus:ring-black focus:outline-none'}),
            'image': forms.URLInput(attrs={'class': 'w-full bg-white border border-gray-200 rounded-xl px-3 py-2 text-xs focus:ring-1 focus:ring-black focus:outline-none'}),
        }

class CheckoutForm(forms.Form):
    guest_name = forms.CharField(max_length=255)
    guest_email = forms.EmailField()
    phone_number = forms.CharField(max_length=20)
    shipping_address = forms.CharField(widget=forms.Textarea)
    payment_method = forms.ChoiceField(choices=Order.PAYMENT_METHOD_CHOICES, default='cod')
    sender_number = forms.CharField(max_length=20, required=False)
    transaction_id = forms.CharField(max_length=100, required=False)
