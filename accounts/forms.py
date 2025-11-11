from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth import get_user_model
from allauth.account.forms import SignupForm, LoginForm
from phonenumber_field.formfields import PhoneNumberField
from django import forms
from django.utils.translation import gettext_lazy as _

import random
from .models import PhoneVerification
from .sms_service import send_sms_verification

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'phone_number',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'phone_number','first_name', 'last_name', )


class CustomSignupForm(SignupForm):
    phone_number = PhoneNumberField(
        label=_('Phone Number'),
        widget=forms.TextInput(attrs={'place_holder': '+989123456789'}))

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if self.Meta.model.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(_("This phone number already exists."))
        return phone_number
    
    def save(self, request):
        user = super().save(request)
        user.phone_number = self.clean_phone_number()
        user.save()

        self.send_verification_code(user.phone_number)

        return user

    def send_verification_code(self, phone_number):
        code = str(random.randint(100000, 999999))
        PhoneVerification.objects.create(
            phone_number=phone_number,
            code=code,
        )
        send_sms_verification(phone_number, code)


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].label = _('Email or Phone Number')
