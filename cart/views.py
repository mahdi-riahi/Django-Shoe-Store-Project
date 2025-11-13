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
            'quantity': item['quantity'],
        })
    return render(request, 'cart/cart_detail.html', {'my_cart':cart})

@require_POST
def cart_update_view(request, variant_id):
    variant = get_object_or_404(ProductVariant, pk=variant_id)
    form = UpdateCartForm(request.POST)

    if form.is_valid():
        cleaned_data = form.cleaned_data
        quantity = cleaned_data.get('quantity')

        if variant.is_available(quantity):
            cart = Cart(request)
            cart.add(variant=variant, quantity=quantity, update=True)
            messages.success(request, _('Cart updated successfully'))

        else:
            messages.error(request, _('Product does not have enough variants'))

        return redirect('cart:cart_detail')

    messages.error(request, _('Form is not valid'))
    return redirect('cart:cart_detail')


@require_POST
def cart_add_view(request, pk):
    product = get_object_or_404(Product, pk=pk)

    color = request.POST.get('color')
    if color:
        variants = product.variants.filter(color=color, is_active=True).order_by('size')
        size_choices = [(variant.size, variant.get_size_display) for variant in variants]

    else:
        size_choices = []

    form = AddToCartForm(
        request.POST,
        size_choices=size_choices,
    )

    if form.is_valid():
        cleaned_data = form.cleaned_data
        quantity = cleaned_data.get('quantity')
        color = cleaned_data.get('color')
        size = cleaned_data.get('size')

        try:
            variant = product.variants.get(color=color, size=size, is_active=True)

            # Check if enough quantity is available
            if variant.is_available(quantity):
                cart = Cart(request)
                cart.add(variant=variant, quantity=quantity)
                messages.success(request, _('Product added to cart successfully!'))
                return redirect('products:product_detail', pk=product.id)

            else:
                pass

        except ProductVariant.DoesNotExist:
            messages.error(request, _('Selected variant is not available.'))

        except Exception as e:
            messages.error(request, _('An error occurred while adding to cart'))

    else:
        messages.error(request, _('Please correct the errors in the form.'))
        print(f'form_errors:{form.errors}')

    return redirect('products:product_detail', pk=pk)

def cart_remove_product_view(request, variant_id):
    variant = get_object_or_404(ProductVariant, pk=variant_id)
    cart = Cart(request)
    cart.remove(variant)
    return redirect('cart:cart_detail')


def cart_clear_view(request):
    cart = Cart(request)
    cart.clear()
    return redirect('products:product_list')
