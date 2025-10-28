from django.contrib import admin

from .models import Product, Comment, WomenVariant, MenVariant, BagVariant, AccessoryVariant, ClothingVariant, ShoesCareVariant, Cover


# Create Inlines
class CoverInline(admin.StackedInline):
    model = Cover
    extra = 1


class MenVariantInline(admin.StackedInline):
    model = MenVariant
    extra = 1


class WomenVariantInline(admin.StackedInline):
    model = WomenVariant
    extra = 1


class BagVariantInline(admin.StackedInline):
    model = BagVariant
    extra = 1


class ShoesCareVariantInline(admin.StackedInline):
    model = ShoesCareVariant
    extra = 1


class AccessoryVariantInline(admin.StackedInline):
    model = AccessoryVariant
    extra = 1


class ClothingVariantInline(admin.StackedInline):
    model = ClothingVariant
    extra = 1


# Create model-admin
class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('title', 'category', 'price', 'is_active')
    ordering = ('is_active', )

    inlines = [
        CoverInline,
        WomenVariantInline,
        MenVariantInline,
        BagVariantInline,
        ClothingVariantInline,
        AccessoryVariantInline,
    ]


class CommentAdmin(admin.ModelAdmin):
    model = Comment
    list_display = ('user', 'product__title', 'datetime_created', )
    ordering = ('datetime_created', )


class CoverAdmin(admin.ModelAdmin):
    model = Comment
    list_display = ('product__title', )
    ordering = ('product', )


admin.site.register(Product, ProductAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Cover, CoverAdmin)
