from django import forms
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from products.models import ProductVariant


class AddToCartForm(forms.Form):
    QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 31)]
    quantity = forms.TypedChoiceField(choices=QUANTITY_CHOICES, coerce=int)
    color = forms.TypedChoiceField(choices=ProductVariant.COLORS, coerce=str, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        # Extract size_choices from kwargs before calling super()
        size_choices = kwargs.pop('size_choices', [])
        super().__init__(*args, **kwargs)

        # Add the size field with dynamic choices
        self.fields['size'] = forms.TypedChoiceField(
            choices=size_choices,
            coerce=int,
            required=True,
            label=_('Size')
        )

class UpdateCartForm(forms.Form):
    QUANTITY_CHOICES = [(i, str(i)) for i in range(1,31)]
    variant_id = forms.IntegerField(validators=[MinValueValidator(0), ], widget=forms.HiddenInput)
    quantity = forms.TypedChoiceField(choices=QUANTITY_CHOICES, coerce=int)
