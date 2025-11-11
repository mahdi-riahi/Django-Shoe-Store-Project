from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class CustomUserFavorite(models.Model):
    user = models.ForeignKey(verbose_name=_('User'), to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(verbose_name=_('Product'), to="products.Product", on_delete=models.CASCADE, related_name='liked_by_users')
    datetime_created = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product', ]

    def __str__(self):
        return f'{self.user}-{self.product}'
