from django.contrib import admin

from .models import Product, ProductColor, ProductColorVariant, Comment, Cover


class CommentAdmin(admin.ModelAdmin):
    model = Comment
    list_display = ('user', 'product__title', 'datetime_created', )
    ordering = ('datetime_created', )


class CoverAdmin(admin.ModelAdmin):
    model = Comment
    list_display = ('product__title', )
    ordering = ('product', )


class CoverInline(admin.StackedInline):
    model = Cover
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('title', 'category', 'price', 'is_active')
    ordering = ('is_active', )

    inlines = [
        CoverInline,
    ]


class ProductColorVariantInline(admin.TabularInline):
    model = ProductColorVariant
    extra = 2


class ProductColorAdmin(admin.ModelAdmin):
    model = ProductColor

    inlines = [
        ProductColorVariantInline,
    ]


admin.site.register(Comment, CommentAdmin)
admin.site.register(Cover, CoverAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductColor, ProductColorAdmin)
