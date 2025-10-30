from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


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
        # Shoes Group
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
            ('Handbag', _('Handbag')),
            ('Shoulder bags', _('Shoulder bags')),
            ('office bag', _('office bag')),
            ('travel bag', _('travel bag')),
            ('backpack', _('backpack')),
            ('card holder', _('card holder')),
            ('coat bag', _('coat bag')),
            ('Checkbook bag', _('Checkbook bag')),
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
            ('medical-insole', _('Medical Insole')),
             ('wax', _('Wax')),
        )),
    )

    title = models.CharField(_('Title'), max_length=150)
    short_description = models.CharField(_('Short Description'), max_length=700)
    description = models.TextField(_('Description'), )
    price = models.PositiveIntegerField(_('Price'), )
    is_active = models.BooleanField(_('Is The Product Active ?'), default=True)
    sell_count = models.PositiveIntegerField(_('How many items of this product were sold?'))
    
    category = models.CharField(_('Category'), max_length=50, choices=CATEGORIES)
    major_category = models.CharField(_('Major Category'), max_length=20, choices=MAJOR_CATEGORIES, blank=True)
    
    datetime_created = models.DateTimeField(_('Datetime Created'), auto_now_add=True)
    datetime_modified = models.DateTimeField(_('Datetime Modified'), auto_now=True)
    user = models.ForeignKey(verbose_name=_('User'), to=get_user_model(), on_delete=models.CASCADE, related_name='products')

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

    # def get_variants(self):
    #     if self.major_category == 'Women':
    #         return self.women_variants
    #     if self.major_category == 'Men':
    #         return self.men_variants
    #     if self.major_category == 'Bags':
    #         return self.bags_variants
    #     if self.major_category == 'Clothing':
    #         return self.clothing_variants
    #     if self.major_category == 'Accessory':
    #         return self.accessory_variants
    #     return self.shoescare_variants

    # @property
    # def active_variants(self):
    #     return self.get_variants().filter(is_active=True)
    #
    # def get_active_variants_get_color_display(self):
    #     colors_list = []
    #     for variant in self.active_variants:
    #         if variant.get_color_display not in colors_list:
    #             colors_list.append(variant.get_color_display)
    #     return colors_list
    #
    # def get_active_variants_colors(self):
    #     colors_list = {}
    #     for variant in self.active_variants:
    #         if variant.color not in colors_list:
    #             colors_list[variant.color] = variant.get_color_display
    #     return colors_list
    #
    # def get_active_variants_info_based_on_colors_dict(self):
    #     colors = self.get_active_variants_colors()
    #     result = {}
    #     for color,color_display in colors.items():
    #         result[color_display] = self.get_variants().filter(color=color, is_active=True)
    #     return result

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
        self.is_active = True if self.colors.filter(is_active=True) else False

    # Add after implementing order & order-item
    # def get_sell_count(self):
    #     return sum(item.quantity for item in self.order_items.all())


class ProductColor(models.Model):
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
    color = models.CharField(_('Color'), max_length=20, choices=COLORS)
    product = models.ForeignKey(verbose_name=_('Product'), to=Product, on_delete=models.CASCADE, related_name='colors')
    is_active = models.BooleanField(_('Is Active'), default=True)

    def __str__(self):
        return f'Product: {self.product}- Color:{self.get_color_display()}'

    def sync_is_active_and_variant(self):
        """
        Set 'is_active' False if there is no active variants
        """
        self.is_active = True if self.variants.filter(is_active=True) else False


class ProductColorVariant(models.Model):
    SIZES = (
        # Shoes Group
        ('Women', (
            (36, 36),
            (37, 37),
            (38, 38),
            (39, 39),
            (40, 40),
            (41, 41),
            (42, 42),
        )),

        ('Men', (
            (40, 40),
            (41, 41),
            (42, 42),
            (43, 43),
            (44, 44),
            (45, 45),
            (46, 46),
            (47, 47),
        )),

        ('Bags', (
            (1, 'Small'),
            (2, 'Medium'),
            (3, 'Large'),
        )),

        ('Clothing', (
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
        )),

        ('Accessory', (
            (85, _('85 cm')),
            (95, _('95 cm')),
            (105, _('105 cm')),
            (115, _('115 cm')),
            (125, _('125 cm')),
            (135, _('135 cm')),
        )),

        ('ShoesCare', (
            (36, 36),
            (37, 37),
            (38, 38),
            (39, 39),
            (40, 40),
            (41, 41),
            (42, 42),
            (40, 40),
            (41, 41),
            (42, 42),
            (43, 43),
            (44, 44),
            (45, 45),
        )),
    )

    size = models.PositiveIntegerField(_('Size'), choices=SIZES)
    quantity = models.PositiveIntegerField(_('Quantity'), default=1, validators=[MinValueValidator(0), ])
    is_active = models.BooleanField(_('Is Active'), default=True)
    color = models.ForeignKey(verbose_name=_('Color'), to=ProductColor, on_delete=models.CASCADE, related_name='variants')

    def __str__(self):
        return f'{self.color} - Size: {self.size} - Quantity: {self.quantity}'

    def sync_is_active_and_quantity(self):
        """
        Set 'is_active' False if quantity equals 0
        Use when quantity amount changes
        """
        self.is_active = False if self.quantity == 0 else True

    def is_addable_to_cart(self, value):
        """
        Check if variant item can be added to cart
        """
        return value <= self.quantity


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
    user = models.ForeignKey(verbose_name=_('User'), to=get_user_model(), on_delete=models.CASCADE, related_name='comments', blank=True, null=True)
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
