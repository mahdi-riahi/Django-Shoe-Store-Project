from django import forms


class AddUpdateCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=30)
    update = forms.BooleanField(required=False)
