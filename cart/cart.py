from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from products.models import ProductVariant


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
        # Fix updating variant quantities

        # Update variant quantities based on variant.is_addable_to_cart
        # self.update_variant_quantities()

    def save(self):
        """
        Mark session as modified to save changes
        """
        self.session.modified = True

    def add(self, variant, quantity=1, update=False):
        """
        Add product variant to cart
        """
        if not variant.is_available(quantity):
            messages.error(self.request, _('Addition to cart failed. Not enough variant in store.'))
            return

        if variant.id not in self.cart:
            self.cart[variant.id] = {'quantity': 0}
        if not update:
            self.cart[variant.id]['quantity'] += quantity
            messages.success(self.request, _('Product added to cart successfully'))

        if update:
            self.cart[variant.id]['quantity'] = quantity
            messages.success(self.request, _('Product quantity in cart updated'))

        self.save()

    def remove(self, variant):
        """
        Remove variant from cart
        """
        if variant.id in self.cart:
            del self.cart[variant.id]
            messages.success(self.request, _('Product variant removed from cart successfully'))
            self.save()
            return
        messages.info(self.request, _('Product variant is not in cart'))
        return

    def clear(self):
        """
        Clear the cart and remove all items from it
        """
        if self.cart:
            del self.session['cart']
            messages.success(self.request, _('Your cart is successfully empty'))
            self.save()
            return
        messages.info(self.request, _('Your cart is already empty'))

    def __len__(self):
        return sum(value['quantity'] for value in self.cart.values())

    def __iter__(self):
        """
        Iterate over cart items and yield product/variant info
        """
        variants = self.get_variant_objects()
        cart = self.cart.copy()

        for variant in variants:
            cart[variant.id]['product_obj'] = variant.product
            cart[variant.id]['variant_obj'] = variant

        for item in cart.values():
            yield item

    def get_variant_objects(self):
        """
        Get all variants in the cart (in a list)
        """
        variant_ids = [variant_id for variant_id in self.cart.keys()]
        return ProductVariant.objects.filter(id__in=variant_ids)

    def update_variant_quantities(self):
        """
        Update variants quantities if variants aren't available (if variant is added to someone else's order)
        """
        for item in self.cart:
            variant = item['variant_obj']
            if not variant.is_available(item['quantity']):
                self.add(variant, variant.quantity, update=True)

    def get_total_price_no_offer(self):
        """
        Calculate total price without discount
        """
        return sum(item['quantity'] * item['product_obj'].price for item in self.cart)

    def get_total_price(self):
        """
        Calculate total price with discount (offer price)
        :param self:
        :return:
        """
        return sum(item['quantity'] * item['product_obj'].offer_price for item in self.cart)
