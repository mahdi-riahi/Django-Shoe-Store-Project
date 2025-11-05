from django.views import generic
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import CustomUserFavorite


class ProfileView(LoginRequiredMixin, generic.DetailView):
    template_name = 'accounts/profile.html'
    context_object_name = 'user_profile'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_orders'] = self.request.user.orders.all()[:5]
        context['favorites_count'] = self.request.user.favorites.count()
        return context


class ProfileUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'accounts/profile_update.html'
    model = get_user_model()
    fields = ['profile_photo', 'first_name', 'last_name', 'username', 'email', 'phone_number', ]
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        """Ensure users can only edit their own profile"""
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, _('Your profile updated successfully'))
        super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('Please correct the errors below.'))
        super().form_valid(form)


class PaymentListView(LoginRequiredMixin, generic.ListView):
    template_name = 'payment/payment_history.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return self.request.user.orders.exclude(zarinpal_authority="")


class FavoriteListView(LoginRequiredMixin, generic.ListView):
    template_name = 'accounts/favorites.html'
    context_object_name = 'favorite_products'

    def get_queryset(self):
        return self.request.user.favorites.all()

# Need Working
class FavoriteCreateView(generic.CreateView):
    model = CustomUserFavorite

# Need Working
class FavoriteDeleteView(generic.DeleteView):
    model = CustomUserFavorite
