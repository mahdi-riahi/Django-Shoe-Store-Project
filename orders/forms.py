from django import forms
from django.utils.translation import gettext_lazy as _

from orders.models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name','last_name','email','phone_number','address','notes',]
        widgets = {
            'address': forms.Textarea(attrs={'rows':5, 'placeholder': _('Please enter your full address')}),
            'notes': forms.Textarea(attrs={'rows': 4, })
        }
