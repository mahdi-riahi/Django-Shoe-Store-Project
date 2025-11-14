from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'placeholder': 'Enter a strong password',
        }),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'placeholder': 'Confirm your password',
        }),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = CustomUser
        fields = ("email", "phone_number", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = _('Enter your @ email')
        self.fields['phone_number'].widget.attrs['placeholder'] = _('ex: 09123456789')


class AdminUserCreationForm(UserCreationForm):
    """
    User creation form for admin without need for phone_verification
    """
    class Meta:
        model = CustomUser
        fields = ('email', 'phone_number', 'username', 'phone_verified')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_phone_verified = self.cleaned_data.get('is_phone_verified', False)
        user.email_verified = True

        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'


class PhoneVerificationForm(forms.Form):
    code = forms.CharField(max_length=6, min_length=6)


class LoginForm(forms.Form):
    email_or_phone = forms.CharField(label=_('Email or Phone Number'), max_length=50, min_length=5)
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
