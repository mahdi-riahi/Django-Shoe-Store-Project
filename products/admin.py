from django.contrib import admin

from .models import Product, Comment, ShoesVariant, BagVariant, ToolVariant, AccessoryVariant, ClotheVariant, Cover


# Create Inlines
class CoverInline(admin.StackedInline):
    model = Cover
    extra = 1


class ShoesVariantInline(admin.StackedInline):
    model = ShoesVariant
    extra = 1


class BagVariantInline(admin.StackedInline):
    model = BagVariant
    extra = 1


class ToolVariantInline(admin.StackedInline):
    model = ToolVariant
    extra = 1


class AccessoryVariantInline(admin.StackedInline):
    model = AccessoryVariant
    extra = 1


class ClotheVariantInline(admin.StackedInline):
    model = ClotheVariant
    extra = 1


# Create model-admin
class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('title', 'category', 'price', 'is_active')
    ordering = ('is_active', )

    inlines = [
        CoverInline,
        ToolVariantInline,
        BagVariantInline,
        ShoesVariantInline,
        ClotheVariantInline,
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
