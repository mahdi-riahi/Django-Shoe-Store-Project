from django.contrib import admin

from .models import Product, ProductVariant, Comment, Cover


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


class ProductVariantInline(admin.StackedInline):
    model = ProductVariant
    extra = 0


# admin.py
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        offer = cleaned_data.get('offer')
        offer_price = cleaned_data.get('offer_price')
        price = cleaned_data.get('price')

        if offer and not offer_price:
            raise ValidationError({
                'offer_price': 'Offer price is required when product is on offer.'
            })

        if offer and offer_price and offer_price >= price:
            raise ValidationError({
                'offer_price': 'Offer price must be less than the original price.'
            })

        return cleaned_data


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ['title', 'price', 'offer', 'offer_price', 'is_active']
    list_editable = ['offer', 'offer_price']
    inlines = [
        CoverInline,
        ProductVariantInline,
    ]


admin.site.register(Comment, CommentAdmin)
admin.site.register(Cover, CoverAdmin)
# admin.site.register(Product, ProductAdmin)
