from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from datetime import timedelta


class PhoneVerification(models.Model):
    phone_number = PhoneNumberField(verbose_name=_('Phone Number'))
    code = models.CharField(_('Code'), max_length=6)
    datetime_created = models.DateTimeField(_('Created At'), auto_now_add=True)
    is_used = models.BooleanField(_('Is used?'), default=False)

    def __str__(self):
        return f'{self.phone_number}-{self.code}'

    def is_expired(self):
        return timezone.now() > self.datetime_created + timedelta(minutes=2)


class CustomUser(AbstractUser):
    email = models.EmailField(_('Email Address'), unique=True)
    phone_number = PhoneNumberField(verbose_name=_('Phone Number'), unique=True, region='IR')
    phone_verified = models.BooleanField(_('Phone Verified'), default=False)

    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    def __str__(self):
        return self.email
