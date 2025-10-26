from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator


class ActiveModelManager(models.Manager):
    def get_queryset(self):
        return super(ActiveModelManager, self).get_queryset().exclude(is_active=False)


class Product(models.Model):
    # CATEGORIES1 = (
    #     ('Shoes', (
    #         ('Women Shoes', (
    #             ('w-summer', _('Summer')),
    #             ('w-casual', _('Casual')),
    #             ('w-sport', _('Sport')),
    #             ('w-medical', _('Medical')),
    #             ('w-sport', _('Sport')),
    #             ('w-formal', _('Formal')),
    #             ('w-majlesi', _('Majlesi')),
    #             ('w-winter', _('Winter')),
    #         )),
    #         ('Men Shoes', (
    #             ('m-summer', _('Summer')),
    #             ('m-casual', _('Casual')),
    #             ('w-sport', _('Sport')),
    #             ('w-medical', _('Medical')),
    #             ('w-sport', _('Sport')),
    #             ('w-formal', _('Formal')),
    #             ('w-majlesi', _('Majlesi')),
    #             ('w-winter', _('Winter')),
    #         ))
    #     )),
    #
    #     ('Purse', (
    #         ('women_purse', _('Women Purse')),
    #         ('men_purse', _('Men Purse')),
    #         ('bags', _('Bags')),
    #     )),
    #
    #     ('Wearing', (
    #         ('coat', _('Coat')),
    #         ('hat', _('Hat')),
    #     )),
    #
    #     ('Accessory', (
    #         ('Belt', (
    #             ('women_belt', _('Women Belt')),
    #             ('men_belt', _('Men Belt')),
    #             ('kids_belt', _('Kids Belt')),
    #         )),
    #         ('Wallet', (
    #             ('wallet', _('Wallet')),
    #             ('keyhan', _('Keyhan')),
    #             ('hand_bag', _('Hand Bag')),
    #         )),
    #         ('Card', _('Card')),
    #         ('buttom', _('Buttom')),
    #     )),
    #
    #     ('Tool', (
    #         ('polish', _('Polish')),
    #     )),
    # )
    CATEGORIES = (
        # Shoes Group
        ('Shoes', (
            ('w-summer', _('Women Summer Shoes')),
            ('w-casual', _('Women Casual Shoes')),
            ('w-sport', _('Women Sport Shoes')),
            ('w-medical', _('Women Medical Shoes')),
            ('w-formal', _('Women Formal Shoes')),
            ('w-majlesi', _('Women Majlesi Shoes')),
            ('w-winter', _('Women Winter Shoes')),
            ('m-summer', _('Men Summer Shoes')),
            ('m-casual', _('Men Casual Shoes')),
            ('m-sport', _('Men Sport Shoes')),
            ('m-medical', _('Men Medical Shoes')),
            ('m-formal', _('Men Formal Shoes')),
            ('m-majlesi', _('Men Majlesi Shoes')),
            ('m-winter', _('Men Winter Shoes')),
        )),

        # Bags Group
        ('Bags', (
            ('women_purse', _('Women Purse')),
            ('men_purse', _('Men Purse')),
            ('bags', _('Bags')),
        )),

        # Clothes Group
        ('Clothes', (
            ('coat', _('Coat')),
            ('hat', _('Hat')),
        )),

        # Accessory Group
        ('Accessories', (
            ('women_belt', _('Women Belt')),
            ('men_belt', _('Men Belt')),
            ('kids_belt', _('Kids Belt')),
            ('wallet', _('Wallet')),
            ('keyhan', _('Keyhan')),
            ('hand_bag', _('Hand Bag')),
            ('card', _('Card Holder')),
            ('buttom', _('Buttom')),
        )),

        # Tools Group
        ('Tools', (
            ('polish', _('Polish')),
        )),
    )

    title = models.CharField(_('Title'), max_length=150)
    short_description = models.CharField(_('Short Description'), max_length=700)
    description = models.TextField(_('Description'), )
    price = models.PositiveIntegerField(_('Price'), )
    is_active = models.BooleanField(_('Is The Product Active ?'), default=True)
    
    category = models.CharField(_('Category'), max_length=50, choices=CATEGORIES)
    
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

    @property
    def variants(self):
        major_cat = self.get_major_category()
        if major_cat == 'Shoes':
            return self.shoes_variants
        if major_cat == 'Bags':
            return self.bags_variants
        if major_cat == 'Clothes':
            return self.clothes_variants
        if major_cat == 'Accessories':
            return self.accessories_variants
        return self.tools_variants

    def sync_is_active_if_no_variant(self):
        """
        Set 'is_active' False if there is no active variant
        """
        variants = self.variants
        self.is_active = True if variants.filter(is_active=True) else False


class Cover(models.Model):
    product = models.ForeignKey(verbose_name=_('Product'), to=Product, on_delete=models.CASCADE, related_name='covers')
    cover = models.ImageField(_('Product Cover'), upload_to='products/covers/')

    def __str__(self):
        return str(self.product)


class ProductVariant(models.Model):
    """
    Abstract base model for product variants
    Represents specific versions of a product (color, size, etc.)
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
        ('cm', _('Cream')),
    )

    color = models.CharField(_('Color'), max_length=2, choices=COLORS, null=True, blank=True)
    quantity = models.PositiveIntegerField(_('Quantity'), validators=[MinValueValidator(0)])
    is_active = models.BooleanField(_('Is the variant active?'), default=True)

    class Meta:
        abstract = True

    def sync_is_active_if_no_storage(self):
        """
        Set 'is_over' True if quantity equals 0
        Use when quantity amount changes
        """
        self.is_active = False if self.quantity == 0 else True

    def is_addable_to_cart(self, value):
        """
        Check if variant item can be added to cart
        """
        return value <= self.quantity


class ShoesVariant(ProductVariant):
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
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, related_name='shoes_variants')
    size = models.PositiveIntegerField(_('Size'), choices=SHOES_SIZES, null=True, blank=True)

    def __str__(self):
        return str(self.product)


class BagVariant(ProductVariant):
    PURSE_SIZES = (
        (1, 'Small'),
        (2, 'Medium'),
        (3, 'Large'),
    )
    
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, related_name='bags_variants')
    size = models.PositiveIntegerField(_('Size'), choices=PURSE_SIZES, null=True, blank=True)

    def __str__(self):
        return str(self.product)


class ClotheVariant(ProductVariant):
    WEARING_SIZES = (
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
    
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, related_name='clothes_variants')
    size = models.PositiveIntegerField(_('Size'), choices=WEARING_SIZES, null=True, blank=True)

    def __str__(self):
        return str(self.product)


class AccessoryVariant(ProductVariant):
    ACCESSORY_SIZES = (
        (85, _('85 cm')),
        (95, _('95 cm')),
        (105, _('105 cm')),
        (115, _('115 cm')),
        (125, _('125 cm')),
        (135, _('135 cm')),
    )
    
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, related_name='accessories_variants')
    size = models.PositiveIntegerField(_('Size'), choices=ACCESSORY_SIZES, null=True, blank=True)

    def __str__(self):
        return str(self.product)


class ToolVariant(ProductVariant):
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, related_name='tools_variants')

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

    user = models.ForeignKey(verbose_name=_('User'), to=get_user_model(), on_delete=models.CASCADE, related_name='comments')
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
