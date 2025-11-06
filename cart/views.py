from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.translation import gettext as _

from products.models import Product, ProductVariant
from .cart import Cart
from .forms import AddUpdateCartForm


def cart_detail_view(request):
    cart = Cart(request)
    for item in cart:
        item['form'] = AddUpdateCartForm(initial={
            'quantity': item['quantity'],
            'update': True,
        })
    return render(request, 'cart/cart_detail.html', {'my_cart':cart})

@require_POST
def cart_add_update_view(request, variant_id):
    variant = get_object_or_404(ProductVariant, pk=variant_id)
    product = variant.product
    form = AddUpdateCartForm(request.POST)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        quantity = cleaned_data.get('quantity')
        update = bool(cleaned_data.get('update'))
        cart = Cart(request)
        cart.add(variant, quantity, update)
        if update:
            return redirect('cart:cart_detail')
        return redirect('product:product_detail', pk=product.id)

    messages.error(request, _('Form is not valid'))
    return redirect('product:product_detail', pk=product.id)


def cart_remove_product_view(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = Cart(request)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_clear_view(request):
    cart = Cart(request)
    cart.clear()
    return redirect('products:product_list')
