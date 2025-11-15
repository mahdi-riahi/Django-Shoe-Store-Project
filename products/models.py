from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


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
    material = models.CharField(_('Materials'), max_length=400, blank=True)
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
        return reverse("products:product_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        # First, validate the model
        self.full_clean()

        # Save first to get a primary key
        super().save(*args, **kwargs)

        # Now we can safely check variants (only for existing products)
        if self.pk:  # Only if product has been saved and has a primary key
            has_active_variants = self.variants.filter(is_active=True).exists()
            if self.is_active != has_active_variants:
                self.is_active = has_active_variants
                # Save again if changed, but avoid infinite recursion
                super().save(update_fields=['is_active'])

            self.sell_count = self.get_sell_count()
            super().save(update_fields=['sell_count'])

        self.major_category = self.get_major_category()
        if not self.offer:
            self.offer_price = self.price
        super().save(update_fields=['major_category', 'offer_price', ])

    def clean(self):
        super().clean()

        if self.offer:

            if not self.offer_price:
                raise ValidationError({
                    'offer_price': _('Offer price is required when offer is True')
                })
            if self.offer_price <= 0:
                raise ValidationError({
                    'offer_price': _('Offer price must be a positive number')
                })
            if self.offer_price >= self.price:
                raise ValidationError({
                    'offer_price': _('Offer price must be lower than price')
                })


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
        """
        Get categories in each major category by having major_category
        """
        for key, values in cls.CATEGORIES:
            if key == major_category:
                categories = {value[0]:value[1] for value in values}
                return categories
        return None

    @classmethod
    def get_major_categories_list(cls):
        """
        A class method to get all major categories in a list
        """
        return [group_name for group_name, subgroups in cls.CATEGORIES]

    @classmethod
    def get_categories_list(cls):
        """
        A class method to get all categories of the model in a list
        """
        categories_list = []
        for group_name, subgroups in cls.CATEGORIES:
            for value, label in subgroups:
                categories_list.append(value)
        return categories_list

    @classmethod
    def find_category_display_from_category(cls, category):
        for group_name, subgroups in cls.CATEGORIES:
            for value, label in subgroups:
                if value == category:
                    return label
        return None

    @classmethod
    def find_category_from_category_display(cls, display):
        for group_name, subgroups in cls.CATEGORIES:
            for value, label in subgroups:
                if label == display:
                    return value
        return None

    def sync_is_active_and_variants(self):
        """
        Set 'is_active' False if there is no active variants
        """
        self.is_active = True if self.variants.filter(is_active=True) else False
        self.save()

    def get_sell_count(self):
        """
        Calculate how many variants from product were sold (from order_items)
        """
        sell_count = 0
        for variant in self.variants.all():
            for item in variant.order_items.all():
                sell_count += item.quantity
        return sell_count

    @property
    def active_variants(self):
        return self.variants.filter(is_active=True)

    def get_active_variants_colors(self):
        colors = {}
        for variant in self.active_variants:
            if variant.color not in colors:
                colors[variant.color] = variant.get_color_display()
        return colors

    def get_active_variants_sizes(self):
        sizes = {}
        for variant in self.active_variants:
            if variant.size and variant.size not in sizes:
                sizes[variant.size] = variant.get_size_display()
        return sizes

    def get_offer_percent(self):
        return (self.price - self.offer_price) / self.price * 100


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

    color = models.CharField(_('Color'), max_length=2, choices=COLORS)
    size = models.PositiveIntegerField(_('Size'), choices=SIZES, blank=True, null=True)

    product = models.ForeignKey(verbose_name=_('Product'), to=Product, on_delete=models.CASCADE, related_name='variants')
    quantity = models.PositiveIntegerField(_('Quantity'), default=1, validators=[MinValueValidator(0), ])
    is_active = models.BooleanField(_('Is the variant active?'), default=True)

    class Meta:
        unique_together = ['product', 'color', 'size']  # Prevent duplicates

    def __str__(self):
        return f'{self.product.title} - Color: {self.get_color_display()} - Size: {self.size}'

    def save(self, *args, **kwargs):
        """
        Auto-sync is_active before saving
        """
        self.product.sync_is_active_and_variants()
        super().save(*args, **kwargs)

    def sync_is_active_quantity(self):
        """
        Set variant active based on quantity
        """
        self.as_active = self.quantity > 0
        self.save()
        self.product.sync_is_active_and_variants()

    def is_available(self, requested_quantity):
        """
        Check if variant item can be added to cart
        """
        return requested_quantity <= self.quantity and self.is_active

    def decrease_quantity(self, quantity):
        """
        Decrease the quantity while creating order
        """
        if self.is_available(quantity):
            self.quantity -= quantity
            self.save()
            self.sync_is_active_quantity()

    def increase_quantity(self, quantity):
        self.quantity += quantity
        self.save()


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
