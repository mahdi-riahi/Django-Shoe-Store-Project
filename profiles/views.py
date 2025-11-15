from django.views import generic
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404, redirect

from products.models import Product
from .models import CustomUserFavorite


class ProfileView(LoginRequiredMixin, generic.DetailView):
    template_name = 'profiles/profile.html'
    context_object_name = 'user_profile'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_orders'] = self.request.user.orders.all()[:5]
        context['orders_count'] = self.request.user.orders.count()
        context['favorites_count'] = self.request.user.favorites.count()
        return context


class ProfileUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'profiles/profile_update.html'
    model = get_user_model()
    fields = ['profile_photo', 'first_name', 'last_name', 'username', 'email', 'phone_number', ]
    # success_url = reverse_lazy('profile:profile_detail')

    def get_object(self, queryset=None):
        """Ensure users can only edit their own profile"""
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, _('Your profile updated successfully'))
        super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('Please correct the errors below.'))
        super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('profile:profile_detail')


class PaymentListView(LoginRequiredMixin, generic.ListView):
    template_name = 'payment/payment_history.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return self.request.user.orders.exclude(zarinpal_authority="").order_by('datetime_created')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        successful_payment_orders = self.request.user.orders.exclude(
            zarinpal_authority="",
            zarinpal_ref_id="",
        )
        context['success_payment_orders_count'] = successful_payment_orders.count()

        total = 0
        for order in successful_payment_orders:
            if order.total_price:
                total += order.total_price
            else:
                total += order.get_total_price()
        context['success_payment_total_amount'] = total
        return context


class FavoriteListView(LoginRequiredMixin, generic.ListView):
    template_name = 'profiles/favorites.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        print(self.request.user.favorites.all())
        return self.request.user.favorites.all()


@login_required
def favorite_add_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    previous_url = request.META.get('HTTP_REFERER')

    if not CustomUserFavorite.objects.filter(
        user=request.user,
        product=product,
    ).exists():

        CustomUserFavorite.objects.create(
            user=request.user,
            product=product,
        )
        messages.success(request, _('Product added to favorites'))

    else:
        messages.info(request, _('Product is already in your favorite list'))

    try:
        return redirect(previous_url)
    except:
        return redirect('profile:favorite_list')


@login_required
def favorite_remove_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    previous_url = request.META.get('HTTP_REFERER')

    try:
        favorite = CustomUserFavorite.objects.get(
            user=request.user,
            product=product,
        )
        favorite.delete()
        messages.success(request, _('Product removed from favorites'))

    except CustomUserFavorite.DoesNotExist:
        messages.info(request, _('Product is not in your favorite list'))

    try:
        return redirect(previous_url)
    except:
        return redirect('profile:favorite_list')
