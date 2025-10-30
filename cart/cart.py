from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from products.models import Product, ProductColor, ProductColorVariant


class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.request = request
        self.session = request.session

        cart = self.session.get('cart')
        if not cart:
            self.session['cart'] = {}
        self.cart = cart = self.session['cart']

    def save(self):
        """
        Mark session as modified to save changes
        """
        self.session.modified = True

    def add(self, product_id, color_id, variant_id, quantity=1, replace=False):
        """
        Add product variant to cart
        """
        product = get_object_or_404(Product, pk=product_id)
        try:
            color = product.colors.get(pk=color_id)
            variant = color.variants.get(pk=variant_id)

            if variant.is_addable_to_cart(quantity):
                if product_id not in self.cart:
                    self.cart[product_id] = {}
                if variant_id not in self.cart[product_id]:
                    self.cart[product_id][variant_id] = {'quantity': 0}
                if not replace:
                    self.cart[product_id][variant_id]['quantity'] += quantity
                    messages.success(self.request, _('Product added to cart successfully'))
                else:
                    self.cart[product_id][variant_id]['quantity'] = quantity
                    messages.success(self.request, _('Product quantity in cart updated'))
                self.save()
                return True

            messages.error(self.request, _('Addition to cart failed. Not enough variant in store.'))
            return False

        except ObjectDoesNotExist:
            messages.error(self.request, _('Object not found'))
            return False

    def remove(self, product_id):
        """
        Remove product from cart
        """
        product = get_object_or_404(Product, pk=product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            messages.success(self.request, _('Product removed from cart successfully'))
            self.save()
            return True
        messages.info(self.request, _('Product is not in cart'))
        return False

    def clear(self):
        """
        Clear the cart and remove all items from it
        """
        if self.cart:
            del self.cart
            messages.success(self.request, _('Your cart is successfully empty'))
            self.save()
        messages.info(self.request, _('Your cart is already empty'))

    def __len__(self):
        quantities = []
        for product in self.cart.values():
            for item in product.values():
                quantities.append(item['quantity'])
        return len(quantities)

    def __iter__(self):
        products = self.get_products()
        cart = self.cart

        # Need working
        for product in products:
            cart[product.id]['product_obj'] = product
            # cart[]

        for item in cart.values():
            yield item

    def get_products(self):
        product_ids = [item for item in self.cart.keys()]
        return Product.objects.filter(id__in=product_ids)
