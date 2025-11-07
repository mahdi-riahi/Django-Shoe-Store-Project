from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import HttpResponseNotFound

from products.models import Product, ProductVariant
from .cart import Cart
from .forms import UpdateCartForm, AddToCartForm


def cart_detail_view(request):
    cart = Cart(request)
    for item in cart:
        item['form'] = UpdateCartForm(initial={
            'update': True,
            'variant_id': item['variant_obj'].id,
        })
    return render(request, 'cart/cart_detail.html', {'my_cart':cart})

@require_POST
def cart_update_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = UpdateCartForm(request.POST)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        quantity = cleaned_data.get('quantity')
        variant_id = int(cleaned_data.get('variant_id'))
        variant = get_object_or_404(ProductVariant, pk=variant_id)

        if variant in product.variants.all():
            cart = Cart(request)
            cart.add(variant=variant, quantity=quantity, update=True)

            return redirect('cart:cart_detail')

    messages.error(request, _('Form is not valid'))
    return redirect('products:product_detail', pk=pk)

@require_POST
def cart_add_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = AddToCartForm(request.POST)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        quantity = cleaned_data.get('quantity')
        color = cleaned_data.get('color')
        size = cleaned_data.get('size')

        try:
            variant = product.variants.get(color=color, size=size)
            # variant = ProductVariant.objects.get(color=color, size=size)
            product = variant.product

            cart = Cart(request)
            cart.add(variant=variant, quantity=quantity)

            return redirect('products:product_detail', pk=product.id)

        except ObjectDoesNotExist:
            return HttpResponseNotFound('<h1>Error 404 : Page Not Found</h1>')

    messages.error(request, _('Form is not valid'))
    return redirect('products:product_detail', pk=pk)


def cart_remove_product_view(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = Cart(request)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_clear_view(request):
    cart = Cart(request)
    cart.clear()
    return redirect('products:product_list')
