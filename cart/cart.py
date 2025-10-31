from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from products.models import ProductColorVariant


class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.request = request
        self.session = request.session

        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart
        # Update variant quantities based on variant.is_addable_to_cart
        self.update_variant_quantities()

    def save(self):
        """
        Mark session as modified to save changes
        """
        self.session.modified = True

    def add(self, variant, quantity=1, update=False):
        """
        Add product variant to cart
        """
        if not variant.is_addable_to_cart(quantity):
            messages.error(self.request, _('Addition to cart failed. Not enough variant in store.'))
            return

        product_id = variant.color.product.id
        if product_id not in self.cart:
            self.cart[product_id] = {}
        if variant.id not in self.cart[product_id]:
            self.cart[product_id][variant.id] = {'quantity': 0}
        if not update:
            self.cart[product_id][variant.id]['quantity'] += quantity
            messages.success(self.request, _('Product added to cart successfully'))
        else:
            self.cart[product_id][variant.id]['quantity'] = quantity
            messages.success(self.request, _('Product quantity in cart updated'))
        self.save()
        return

    # def add(self, product_id, color_id, variant_id, quantity=1, update=False):
    #     """
    #     Add product variant to cart
    #     """
    #     product = get_object_or_404(Product, pk=product_id)
    #     try:
    #         color = product.colors.get(pk=color_id)
    #         variant = color.variants.get(pk=variant_id)
    #
    #         if variant.is_addable_to_cart(quantity):
    #             if product_id not in self.cart:
    #                 self.cart[product_id] = {}
    #             if variant_id not in self.cart[product_id]:
    #                 self.cart[product_id][variant_id] = {'quantity': 0}
    #             if not update:
    #                 self.cart[product_id][variant_id]['quantity'] += quantity
    #                 messages.success(self.request, _('Product added to cart successfully'))
    #             else:
    #                 self.cart[product_id][variant_id]['quantity'] = quantity
    #                 messages.success(self.request, _('Product quantity in cart updated'))
    #             self.save()
    #             return True
    #
    #         messages.error(self.request, _('Addition to cart failed. Not enough variant in store.'))
    #         return False
    #
    #     except ObjectDoesNotExist:
    #         messages.error(self.request, _('Object not found'))
    #         return False

    def remove(self, product):
        """
        Remove product from cart
        """
        if product.id in self.cart:
            del self.cart[product.id]
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
            del self.session['cart']
            messages.success(self.request, _('Your cart is successfully empty'))
            self.save()
        messages.info(self.request, _('Your cart is already empty'))

    def __len__(self):
        quantities = []
        for product in self.cart.values():
            for item in product.values():
                quantities.append(item['quantity'])
        return sum(quantities)

    def __iter__(self):
        variants = self.get_variant_objects()
        cart = {variant.id: {
            'variant_obj': variant,
            'color_obj': variant.color,
            'product_obj': variant.color.product,
            'quantity': self.cart[variant.color.product.id][variant.id]['quantity'],
        } for variant in variants}

        for item in cart.values():
            yield item

    def get_variant_objects(self):
        variant_ids = []
        for value in self.cart.values():
            for key in value.keys():
                variant_ids.append(key)
        return ProductColorVariant.objects.filter(id__in=variant_ids)

    # Update variants quantities if variants are not addable to cart (if variant is added to someone else's order)
    def update_variant_quantities(self):
        for item in self.cart:
            variant = item['variant_obj']
            if not variant.is_addable_to_cart(item['quantity']):
                self.add(variant, variant.quantity, update=True)
