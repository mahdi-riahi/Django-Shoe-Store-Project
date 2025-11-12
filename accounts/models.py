import random

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from datetime import timedelta
import random


# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, phone_number, password=None, **extra_fields):
#         if not email:
#             raise ValueError('The Email must be set')
#         if not phone_number:
#             raise ValueError('The Phone Number must be set')
#
#         email = self.normalize_email(email)
#         user = self.model(email=email, phone_number=phone_number, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, email, phone_number, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('is_active', True)
#
#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')
#
#         return self.create_user(email, phone_number, password, **extra_fields)


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
        return self.phone_number

    def is_valid(self):
        return not self.is_used and timezone.now() < self.datetime_expires


class CustomUser(AbstractUser):
    email = models.EmailField(_('Email Address'), unique=True)
    phone_number = PhoneNumberField(verbose_name=_('Phone Number'), unique=True, region='IR')
    phone_verified = models.BooleanField(_('Phone Verified'), default=False)
    email_verified = models.BooleanField(_('Email Verified'), default=False)

    username = models.CharField(_('Username'), max_length=50, null=True, blank=True)
    # username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'username']

    # objects = CustomUserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email
