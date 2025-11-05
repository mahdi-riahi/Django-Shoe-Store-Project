from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator


class ActiveModelManager(models.Manager):
    def get_queryset(self):
        return super(ActiveModelManager, self).get_queryset().exclude(is_active=False)


class Product(models.Model):
    MAJOR_CATEGORIES = (
        ('Women', 'Women'),
        ('Men', 'Men'),
        ('Bags', 'Bags'),
        ('Clothing', 'Clothing'),
        ('Accessory', 'Accessory'),
        ('ShoesCare', 'ShoesCare'),
    )
    CATEGORIES = (
        ('Women', (
            ('w-summer', _('Women Summer Shoes')),
            ('w-casual', _('Women Casual Shoes')),
            ('w-sport', _('Women Sport Shoes')),
            ('w-medical', _('Women Medical Shoes')),
            ('w-formal', _('Women Formal Shoes')),
            ('w-heels', _('Women Heels Shoes')),
            ('w-winter', _('Women Winter Shoes')),
        )),

        ('Men', (
            ('m-summer', _('Men Summer Shoes')),
            ('m-sport', _('Men Sport Shoes')),
            ('m-medical', _('Men Medical Shoes')),
            ('m-formal', _('Men Formal Shoes')),
            ('m-occasional', _('Men Occasional Shoes')),
            ('m-winter', _('Men Winter Shoes')),
        )),

        ('Bags', (
            ('hand-bag', _('Handbag')),
            ('shoulder-bags', _('Shoulder bags')),
            ('office-bag', _('Office bag')),
            ('travel-bag', _('Travel bag')),
            ('back-pack', _('Backpack')),
            ('card-holder', _('Card holder')),
            ('coat-bag', _('Coat bag')),
            ('checkbook-bag', _('Checkbook bag')),
        )),

        ('Clothing', (
            ('m-jackets', _('Men Jackets')),
            ('w-jackets', _('Women Jackets')),
            ('hats', _('Hats')),
        )),

        ('Accessory', (
            ('m-accessories', 'Men'),
            ('w-accessories', 'Women'),
        )),

        ('ShoesCare', (
            ('medical-insole', _('Medical insole')),
             ('wax', _('Wax')),
        )),
    )

    title = models.CharField(_('Title'), max_length=150)
    short_description = models.CharField(_('Short Description'), max_length=700)
    description = models.TextField(_('Description'), )
    price = models.PositiveIntegerField(_('Price'), )
    is_active = models.BooleanField(_('Is The Product Active ?'), default=True)
    sell_count = models.PositiveIntegerField(_('How many items of this product were sold?'), default=0)

    # If product is in offer
    offer = models.BooleanField(_('Does this product have an offer?'), default=False)
    offer_price = models.PositiveIntegerField(_('Offer Price'), null=True, blank=True)
    
    category = models.CharField(_('Category'), max_length=50, choices=CATEGORIES)
    major_category = models.CharField(_('Major Category'), max_length=20, choices=MAJOR_CATEGORIES, blank=True)
    
    datetime_created = models.DateTimeField(_('Datetime Created'), auto_now_add=True)
    datetime_modified = models.DateTimeField(_('Datetime Modified'), auto_now=True)
    user = models.ForeignKey(verbose_name=_('User'), to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')

    # Manager
    objects = models.Manager()
    active_product_manager = ActiveModelManager()

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        # Auto-populate major_category before saving
        self.major_category = self.get_major_category()
        super().save(*args, **kwargs)


    def get_rating_counts(self):
        """
        Calculate how many rates given to product
        """
        return len(self.comments.filter(rate__isnull=False))

    def get_rating_average(self):
        """
        Calculate average rating for product
        """
        comments = self.comments.filter(rate__isnull=False)
        if not comments:
            return 0
        avg_rating = sum(comment.rate for comment in comments) / len(comments)
        return avg_rating

    def get_major_category(self):
        """
        Get the major category group for this product
        """
        for group_name, choices in self.CATEGORIES:
            for value, display_name in choices:
                if value == self.category:
                    return group_name
        return None

    @classmethod
    def get_categories_from_major_cat(cls, major_category):
        for key, values in cls.CATEGORIES:
            if key == major_category:
                return (value[0] for value in values)
        return None

    @classmethod
    def get_major_categories_list(cls):
        return [group_name for group_name, subgroups in cls.CATEGORIES]

    @classmethod
    def get_categories_list(cls):
        categories_list = []
        for group_name, subgroups in cls.CATEGORIES:
            for value, label in subgroups:
                categories_list.append(value)
        return categories_list

    def sync_is_active_and_colors(self):
        """
        Set 'is_active' False if there is no active color
        """
        self.is_active = True if self.variants.filter(is_active=True) else False
        self.save()

    def get_sell_count(self):
        sell_count = 0
        for variant in self.variants.all():
            for item in variant.order_items.all():
                sell_count += item.quantity
        self.sell_count = sell_count
        return sell_count


class ProductVariant(models.Model):
    COLORS = (
        ('we', _('White')),
        ('bk', _('Black')),
        ('yw', _('Yellow')),
        ('rd', _('Red')),
        ('be', _('Blue')),
        ('ce', _('Chocolate')),
        ('bn', _('Brown')),
        ('wn', _('Wheat')),
        ('lw', _('Lightyellow')),
    )

    SIZES = (
        ('Women', tuple((i, str(i)) for i in range(36,43))),

        ('Men', tuple((i, str(i)) for i in range(40,48))),

        ('Bags', (
            (1, 'Small'),
            (2, 'Medium'),
            (3, 'Large'),
        )),

        ('Clothing', tuple((i, str(i)) for i in range(36,63,2))),

        ('Accessory', tuple((i, f'{i}cm') for i in range(85,140,10))),

        ('ShoesCare', tuple((i, str(i)) for i in range(36,46))),
    )

    color = models.CharField(_('Color'), max_length=2, choices=COLORS, blank=True)
    size = models.PositiveIntegerField(_('Size'), choices=SIZES, blank=True, null=True)

    product = models.ForeignKey(verbose_name=_('Product'), to=Product, on_delete=models.CASCADE, related_name='variants')
    quantity = models.PositiveIntegerField(_('Quantity'), default=1, validators=[MinValueValidator(0), ])
    is_active = models.BooleanField(_('Is the variant active?'), default=True)

    class Meta:
        unique_together = ['product', 'color', 'size']  # Prevent duplicates

    def __str__(self):
        return f'{self.product.title} - Color: {self.get_color_display()} - Size: {self.size}'

    def sync_is_active_quantity(self):
        """
        Set variant active based on quantity
        """
        self.as_active = self.quantity > 0
        self.save()

    def is_available(self, requested_quantity):
        """
        Check if variant item can be added to cart
        """
        return requested_quantity <= self.quantity and self.is_active


class Cover(models.Model):
    product = models.ForeignKey(verbose_name=_('Product'), to=Product, on_delete=models.CASCADE, related_name='covers')
    cover = models.ImageField(_('Product Cover'), upload_to='products/covers/')

    def __str__(self):
        return str(self.product)


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

    name = models.CharField(_('Name'), max_length=100, blank=True)
    email = models.EmailField(_('Email'), max_length=100, blank=True)
    user = models.ForeignKey(verbose_name=_('User'), to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments', blank=True, null=True)
    product = models.ForeignKey(verbose_name=_('Product'), to=Product, on_delete=models.CASCADE, related_name='comments')

    text = models.TextField(_('Text'), )

    recommend = models.BooleanField(_('Do you recommend this product to others?'), default=True, choices=RECOMMENDATIONS)
    rate = models.PositiveIntegerField(_('Rate this product from 1-5'), blank=True, null=True, choices=RATINGS)
    is_active = models.BooleanField(_('Is this comment active'), default=True)

    datetime_created = models.DateTimeField(_('Datetime Created'), auto_now_add=True)
    datetime_modified = models.DateTimeField(_('Datetime Modified'), auto_now=True)


    def __str__(self):
        return f'{self.user} - {self.product}'

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"pk": self.product.pk})
