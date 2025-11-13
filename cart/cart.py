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

        # Update variant quantities based on availability
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
        if not variant.is_available(quantity):
            messages.error(self.request, _('Addition to cart failed. Not enough variant in store.'))
            return False

        variant_id = str(variant.id)

        if variant_id not in self.cart:
            self.cart[variant_id] = {'quantity': 0}

        if update:
            self.cart[variant_id]['quantity'] = quantity
            messages.success(self.request, _('Product quantity in cart updated'))

        else:
            new_quantity = self.cart[variant_id]['quantity'] + quantity
            if variant.is_available(new_quantity):
                self.cart[variant_id]['quantity'] += quantity
                messages.success(self.request, _('Product added to cart successfully'))

            else:
                messages.error(self.request, _("Can not add more items. Not enough stock."))
                return False

        self.save()
        return True

    def remove(self, variant):
        """
        Remove variant from cart
        """
        variant_id = str(variant.id)
        if variant_id in self.cart:
            del self.cart[variant_id]
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
            variant_id = str(variant.id)
            cart[variant_id]['product_obj'] = variant.product
            cart[variant_id]['variant_obj'] = variant

        for item in cart.values():
            if 'product_obj' in item and 'variant_obj' in item:
                yield item

    def get_variant_objects(self):
        """
        Get all variants in the cart (in a list)
        """
        variant_ids = [int(variant_id) for variant_id in self.cart.keys()]
        return ProductVariant.objects.filter(id__in=variant_ids)

    def update_variant_quantities(self):
        """
        Update variants quantities if variants aren't available (if variant is added to someone else's order)
        """
        variants = self.get_variant_objects()
        for variant in variants:
            variant_id = str(variant.id)
            current_quantity = self.cart[str(variant_id)]['quantity']
            if not variant.is_available(current_quantity):

                if variant.quantity > 0:
                    self.add(variant, variant.quantity, update=True)
                    messages.warning(self.request,
                                     _('Quantity reduced for %s due to stock limits') % variant.product.title)

                else:
                    self.remove(variant)
                    messages.warning(self.request,
                                     _('%s removed from cart due to stock limits') % variant.product.title)

    def get_total_price_no_offer(self):
        """
        Calculate total price without discount
        """
        return sum(item['quantity'] * item['product_obj'].price for item in self)

    def get_total_price(self):
        """
        Calculate total price with discount (offer price)
        :param self:
        :return:
        """
        return sum(item['quantity'] * item['product_obj'].offer_price for item in self)
