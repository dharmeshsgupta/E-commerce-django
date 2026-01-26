from django import forms
from .models import Order, ReturnRequest

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'address_line_1', 'address_line_2', 'country', 'state', 'city', 'order_note']
        
        
# orders/forms.py
from django import forms
from .models import ReturnRequest

class ReturnForm(forms.ModelForm):
    class Meta:
        model = ReturnRequest
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Please describe why you want to return this item (e.g., Wrong size, Damaged, etc.)'
            }),
        }