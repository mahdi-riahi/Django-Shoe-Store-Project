from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.shortcuts import reverse
from django.core.validators import RegexValidator

from datetime import datetime, timedelta

from products.models import ProductVariant
from cart.cart import Cart


class Order(models.Model):
    STATUSES = (
        (0, _('Not Paid')),
        (1, _('Processing')),
        (2, _('Posted')),
        (3, _('Delivered')),
        (4, _('Canceled')),
        (5, _('Returned')),
    )

    phone_regex = RegexValidator(
        regex=r'^09\d{9}$',
        message=_("Phone number must be exactly 11 digits starting with '09'.")
    )

    first_name = models.CharField(_('First Name'), max_length=100)
    last_name = models.CharField(_('Last Name'), max_length=100)
    email = models.EmailField(_('Email'))
    user = models.ForeignKey(
        verbose_name=_('User'),
        to=get_user_model(),
        on_delete=models.CASCADE,
        related_name='orders'
    )
    phone_number = models.CharField(
        verbose_name=_('Phone Number'),
        max_length=11,
        validators=[phone_regex],
        blank=False,
        null=False,
    )
    address = models.CharField(_('Address'), max_length=700)
    notes = models.CharField(_('Any notes about your order?'), max_length=500, blank=True)
    total_price = models.PositiveIntegerField(_('Total Price'), blank=True, null=True)  # Gets once and final amount when order is activated

    is_paid = models.BooleanField(_('Is order paid?'), default=False)
    status = models.PositiveIntegerField(_('Order Status'), choices=STATUSES, default=0)
    # delivery_date = models.DateField(choices=)

    # Payment Detail
    zarinpal_authority = models.CharField(_('Zarinpal Authority'), max_length=255, blank=True)
    zarinpal_ref_id = models.CharField(_('Zarinpal Reference ID'), max_length=150, blank=True)
    zarinpal_data = models.TextField(_('Zarinpal Data'), blank=True)

    datetime_created = models.DateTimeField(_('Datetime Created'), auto_now_add=True)
    datetime_modified = models.DateTimeField(_('Datetime Modified'), auto_now=True)

    def __str__(self):
        return f'User:{self.user}-Order:{self.id}'

    def __len__(self):
        return sum(item.quantity for item in self.items.all())

    def get_absolute_url(self):
        return reverse('orders:order_detail', kwargs={'pk': self.id})

    def activate_order(self):
        """
        Activate the order when payment is done
        Give onetime amount to self.total_price forever
        """
        self.status = self.STATUSES[1][0]
        self.is_paid = True
        self.total_price = self.get_total_price()
        self.save()

    def get_total_price(self):
        """
        Calculate total price amount of order (Automatic product-price refresh)
        """
        return sum(item.get_total_price() for item in self.items.all())

    def check_expiration(self):
        """
        Check if order is not paid until 15 minutes after order registration and cancel it if so
        :return True if it's expired
        If returns True you can delete the order object
        """
        if self.datetime_created + timedelta(minutes=15) < datetime.now() and not self.is_paid:
            return True
        return False

    def cancel_order_if_payment_failed(self, request):
        """
        Cancel the order and refill the cart with order items
        """
        self.status = self.STATUSES[4][0]
        self.is_paid = False
        self.save()

        # Increase quantity of the variant when order is canceled
        for item in self.items.all():
            item.product_variant.increase_quantity(item.quantity)

        # Refill the cart
        cart = Cart(request)
        for item in self.items.all():
            cart.add(item.product_variant, item.quantity)

    def update_user(self):
        """
        Update user's blank fields with data received from order
        """
        user = self.user
        if not user.first_name:
            user.first_name = self.first_name
        if not user.last_name:
            user.last_name = self.last_name
        if not user.phone_number:
            user.phone_number = self.phone_number
        if not user.email:
            user.email = self.email
        user.save()

    def require_payment(self):
        return not self.is_paid and self.status == 0


class OrderItem(models.Model):
    quantity = models.PositiveIntegerField(_('Quantity'))
    price = models.PositiveIntegerField(_('Price'), blank=True)
    product_variant = models.ForeignKey(verbose_name=_('Product Variant'), to=ProductVariant, on_delete=models.CASCADE, related_name='order_items')
    order = models.ForeignKey(verbose_name=_('Order'), to=Order, on_delete=models.CASCADE, related_name='items')

    def __str__(self):
        return f'Order {self.order.id}-{self.quantity}X{self.price}'

    def save(self, *args, **kwargs):
        """
        Auto-populate price before saving
        """
        self.price = self.product_variant.product.offer_price
        super().save(*args, **kwargs)

    def get_total_price(self):
        """
        Calculate total price and refresh price with related product
        """
        self.save()
        return self.quantity * self.price
