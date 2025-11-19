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


class CustomUserManager(BaseUserManager):
    def create_user(self, email, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email must be set'))
        if not phone_number:
            raise ValueError(_('Phone number must be set'))

        email = self.normalize_email(email)

        if 'username' not in extra_fields:
            extra_fields['username'] = self.generate_username_from_email(email)

        user = self.model(
            email=email,
            phone_number=phone_number,
            **extra_fields,
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save()
        return user

    def create_superuser(self, email, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('phone_verified', True)
        extra_fields.setdefault('email_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))

        self.create_user(email, phone_number, password, **extra_fields)

    def generate_username_from_email(self, email):
        if not email:
            raise ValueError(_('Email required'))

        email_parts = email.split('@')
        base_username =  email_parts[0]

        # Make sure username becomes unique
        temp = 1
        username = base_username
        while self.model.objects.filter(username=username).exists():
            username = base_username + str(temp)
            temp += 1

        return username


class CustomUser(AbstractUser):
    email = models.EmailField(_('Email Address'), unique=True)
    phone_number = PhoneNumberField(verbose_name=_('Phone Number'), unique=True, region='IR')
    phone_verified = models.BooleanField(_('Phone Verified'), default=False)
    email_verified = models.BooleanField(_('Email Verified'), default=False)

    username = models.CharField(_('Username'), max_length=50, null=True, blank=True)

    profile_photo = models.ImageField(_('Profile Photo'), upload_to='profiles/photos/', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', ]

    # Manager
    objects = CustomUserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse('profile:profile_detail')
