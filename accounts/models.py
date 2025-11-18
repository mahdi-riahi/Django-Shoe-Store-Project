from django.shortcuts import reverse
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from datetime import timedelta
import random


class PhoneVerification(models.Model):
    phone_number = PhoneNumberField(verbose_name=_('Phone Number'))
    code = models.CharField(_('Code'), max_length=6)
    datetime_created = models.DateTimeField(_('Created At'), auto_now_add=True)
    datetime_expires = models.DateTimeField(_('Expires At'), blank=True, null=True)
    is_used = models.BooleanField(_('Is used?'), default=False)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(random.randint(100000, 999999))
        if not self.datetime_expires:
            self.datetime_expires = timezone.now() + timedelta(minutes=2)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.phone_number)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.datetime_expires


class CustomUser(AbstractUser):
    email = models.EmailField(_('Email Address'), unique=True)
    phone_number = PhoneNumberField(verbose_name=_('Phone Number'), unique=True, region='IR')
    phone_verified = models.BooleanField(_('Phone Verified'), default=False)
    email_verified = models.BooleanField(_('Email Verified'), default=False)

    username = models.CharField(_('Username'), max_length=50, null=True, blank=True)

    profile_photo = models.ImageField(_('Profile Photo'), upload_to='profiles/photos/', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse('profile:profile_detail')
