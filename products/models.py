from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class ActiveModelManager(models.Manager):
    def get_queryset(self):
        return super(ActiveModelManager, self).get_queryset().exclude(is_active=False)


class Product(models.Model):
    CATEGORIES = (
        ('sh', _('Shoe')),
        ('pu', _('Purse')),
        ('co', _('Coat')),
        ('ec', _('Eccessory')),
        ('to', _('Tools')),
    )

    title = models.CharField(_('Title'), max_length=150)
    short_description = models.CharField(_('Short Description'), max_length=700)
    description = models.TextField(_('Description'), )
    price = models.PositiveIntegerField(_('Price'), )
    is_active = models.BooleanField(_('Is The Product Active ?'), default=True)
    
    category = models.CharField(_('Category'), max_length=3, choices=CATEGORIES)
    
    datetime_created = models.DateTimeField(_('Datetime Created'), auto_now_add=True)
    datetime_modified = models.DateTimeField(_('Datetime Modified'), auto_now=True)
    user = models.ForeignKey(verbose_name=_('User'), to=get_user_model(), on_delete=models.CASCADE, related_name='products')

    # Manager
    objects = models.Manager
    active_product_manager = ActiveModelManager

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"pk": self.pk})
    
    def sync_is_active_if_no_stock(self):
        """
        Set 'is_active' False if there is no active stock
        """
        self.is_active = True if not self.stock.exclude(is_active=False) else False

    def get_rating_counts(self):
        """
        Calculate how many rates given for product
        """
        return len(self.comments.filter(rate__isnull=False))

    def get_rating_average(self):
        """
        Calculate average rating for product
        """
        comments = self.comments.filter(rate__isnull=False)
        if not comments:
            return 0
        avg_rating = float(sum(comment.rate for comment in comments) / len(comments))
        return avg_rating
    

class Cover(models.Model):
    product = models.ForeignKey(_('Product'), Product, on_delete=models.CASCADE, related_name='covers')
    cover = models.ImageField(_('Product Cover'), upload_to='products/covers/')

    def __str__(self):
        return self.product


class Stock(models.Model):
    """
    Stock is an abstract model class made for inheritance
    """
    COLORS = (
        ('we', _('White')),
        ('bk', _('Black')),
        ('yw', _('Yellow')),
        ('re', _('Red')),
        ('be', _('Blue')),
        ('he', _('HoneyLike')),
        ('bn', _('Brown')),
        ('wn', _('Wheaten')),
    )
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, related_name='stock')

    color = models.CharField(_('Color'), max_length=2, choices=COLORS, null=True, blank=True)
    storage = models.PositiveIntegerField(_('Storage'))
    is_active = models.BooleanField(_('Is the stock active?'), default=True)

    class Meta:
        abstract = True
    
    def __str__(self):
        return self.product

    def sync_is_active_if_no_storage(self):
        """
        Set 'is_over' True if storage equals 0
        Use when storage amount changes
        """
        self.is_active = False if self.storage == 0 else True


class ShoeStock(Stock):
    SHOES_SIZES = (
        (36, 36),
        (37, 37),
        (38, 38),
        (39, 39),
        (40, 40),
        (41, 41),
        (42, 42),
        (43, 43),
        (44, 44),
        (45, 45),
        (46, 46),
        (47, 47),
    )
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, related_name='shoes_stock')
    size = models.CharField(_('Size'), choices=SHOES_SIZES, null=True, blank=True)


class PurseStock(Stock):
    PURSE_SIZES = (
        (1, 'Small'),
        (2, 'Medium'),
        (3, 'Large'),
    )
    
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, related_name='purse_stock')
    size = models.CharField(_('Size'), choices=PURSE_SIZES, null=True, blank=True)


class CoatStock(Stock):
    COAT_SIZES = (
        (36, 36),
        (38, 38),
        (40, 40),
        (42, 42),
        (44, 44),
        (46, 46),
        (48, 48),
        (50, 50),
        (52, 52),
        (54, 54),
        (56, 56),
        (58, 58),
        (60, 60),
        (62, 62),
    )
    
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, related_name='coat_stock')
    size = models.CharField(_('Size'), choices=COAT_SIZES, null=True, blank=True)


class BeltStock(Stock):
    BELT_SIZES = (
        (85, _('85 cm')),
        (95, _('95 cm')),
        (105, _('105 cm')),
        (115, _('115 cm')),
        (125, _('125 cm')),
        (135, _('135 cm')),
    )
    
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, related_name='belt_stock')
    size = models.CharField(_('Size'), choices=BELT_SIZES, null=True, blank=True)


class Comment(models.Model):
    RECOMMENDATIONS = (
        (True, _('Yes')),
        (False, _('No')),
    )
    RATINGS = (
        (1, _('1/5  Very Bad')),
        (2, _('2/5  Low Quality')),
        (3, _('3/5  Average')),
        (4, _('4/5  Good')),
        (5, _('5/5  Perfect')),
    )

    user = models.ForeignKey(verbose_name=_('User'), to=get_user_model(), on_delete=models.CASCADE, related_name='comments')
    product = models.ForeignKey(verbose_name=_('Product'), to=Product, on_delete=models.CASCADE, related_name='comments')

    text = models.TextField(_('Text'), )

    recommend = models.BooleanField(_('Do you recommend this product to others?'), default=True, choices=RECOMMENDATIONS)
    rate = models.PositiveIntegerField(_('Rate this product from 1-5'), blank=True, choices=RATINGS)
    is_active = models.BooleanField(_('Is this comment active'), default=True)

    datetime_created = models.DateTimeField(_('Datetime Created'), auto_now_add=True)
    datetime_modified = models.DateTimeField(_('Datetime Modified'), auto_now=True)
    

    def __str__(self):
        return self.product
    
    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"pk": self.product.pk})
