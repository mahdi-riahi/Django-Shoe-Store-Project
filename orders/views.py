from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views import generic
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from orders.models import Order, OrderItem
from cart.cart import Cart
from .forms import OrderCreateForm

@login_required
def order_create_view(request):
    """
    Create a new order + order-items and redirect to order confirm view
    """
    form = OrderCreateForm(request.POST or None)
    if request.method == 'POST':
        cart = Cart(request)
        # Check if cart is empty
        if not cart:
            messages.warning(request, _('Your cart is empty. Please add some products to your cart.'))
            return redirect('products:product_list')

        if form.is_valid:
            # Create order
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            order.update_user()
            # Create order items
            for item in cart:
                OrderItem.objects.create(
                    quantity=item['quantity'],
                    product_variant=item['variant_obj'],
                    order=order,
                )
                # Decrease product variant's quantity
                item['variant_obj'].decrease_quantity(item['quantity'])
            # Empty Cart
            cart.clear()
            # Messaging
            messages.success(request, _('Your order was successfully created'))
            # Redirect to order_confirm url
            return redirect('orders:order_confirm', pk=order.id)

        messages.add_message(request, messages.INFO, _('Some fields in the form are not valid'))

    else:
        if request.user.orders.exists():
            order = request.user.orders.last()
            form = OrderCreateForm(initial={
                'first_name': order.first_name,
                'last_name': order.last_name,
                'email': order.email,
                'phone_number': order.phone_number,
                'address': order.address,
            })

    return render(request, 'orders/order_create.html', {'form': form})


class OrderListView(LoginRequiredMixin, generic.ListView):
    """
    Show all orders with different statuses
    """
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(OrderListView, self).get_context_data()

        processing_statuses = [0, 1, 2,]
        context['processing_orders'] = Order.objects.filter(
            user=self.request.user,
            status__in=processing_statuses
        ).order_by('status')

        context['delivered_orders'] = Order.objects.filter(user=self.request.user, status=3)
        context['canceled_orders'] = Order.objects.filter(user=self.request.user, status=4)
        context['returned_orders'] = Order.objects.filter(user=self.request.user, status=5)

        return context


class OrderDetailView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    """
    Show order details
    If order is not paid yet, show links to order confirm view
    """
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        if self.object.require_payment():
            messages.warning(self.request, _('We can not hold your order more than 15 minutes after its registration'))
            messages.info(self.request, _('Please confirm your order as soon as possible'))
        return super(OrderDetailView, self).get_context_data()

    def test_func(self):
        return self.request.user == self.get_object().user


class OrderUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    """
    Update(edit) the order and redirect to order confirm view
    """
    model = Order
    form_class = OrderCreateForm
    # fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'notes', ]
    template_name = 'orders/order_update.html'

    def test_func(self):
        return self.request.user == self.get_object().user and self.get_object().is_paid == False

    def get_success_url(self):
        return reverse('orders:order_confirm', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        messages.success(self.request, _('Your order was successfully updated'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('Please correct errors below'))
        print(form.errors)
        return super().form_invalid(form)


@login_required
def order_confirm_view(request, pk):
    """
    Finalize and confirm order details and redirect to zarinpal-payment url
    """
    order = get_object_or_404(Order, pk=pk)

    if order.user == request.user:

        # Check if order is already paid before
        if order.is_paid:
            messages.info(request, _('Payment is already done for your order'))
            return redirect('orders:order_detail', pk=pk)

        if order.status !=0:
            messages.info(request, _('This order is not ready for payment. Check its status'))
            return redirect('orders:order_detail', pk=pk)

        # Redirect to payment process
        if request.method == 'POST':
            request.session['order_id'] = order.id
            return redirect('payment:payment_process_sandbox')
        # If method == 'GET'
        # Messaging to the client about how to do the payment
        messages.success(request, _('Confirm your information and go to payment'))
        return render(request, 'orders/order_confirm.html', {'order': order})

    # If user is not order's user
    return HttpResponseForbidden('<h1>ERROR 403 Forbidden</h1>')
