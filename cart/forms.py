from django import forms
from django.core.validators import MinValueValidator

from products.models import ProductVariant


class AddToCartForm(forms.Form):
    QUANTITY_CHOICES = [(i, str(i)) for i in range(1,31)]
    quantity = forms.TypedChoiceField(choices=QUANTITY_CHOICES, coerce=int)
    color = forms.TypedChoiceField(choices=ProductVariant.COLORS, coerce=str, widget=forms.HiddenInput)

    def __init__(self,*args, **kwargs):
        super().__init__(*args,**kwargs)
        # super(AddToCartForm, self).__init__(*args, **kwargs)

        size_choices = [(size, size_display) for size,size_display in kwargs.items()]
        self.fields['size'] = forms.TypedChoiceField(choices=size_choices, coerce=int, required=False)


class UpdateCartForm(forms.Form):
    QUANTITY_CHOICES = [(i, str(i)) for i in range(1,31)]
    variant_id = forms.IntegerField(validators=[MinValueValidator(0), ], widget=forms.HiddenInput)
    quantity = forms.TypedChoiceField(choices=QUANTITY_CHOICES, coerce=int)
