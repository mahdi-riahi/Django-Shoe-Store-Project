from django.urls import path

from . import views


app_name = 'profile'

urlpatterns = [
    path('', views.ProfileView.as_view(), name='profile_detail'),
    path('settings/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('payment_history/', views.PaymentListView.as_view(), name='payment_history'),
    path('favorites/', views.FavoriteListView.as_view(), name='favorite_list'),
    path('favorites/add/', views.FavoriteCreateView.as_view(), name='favorite_create'),
    path('favorites/remove/', views.FavoriteDeleteView.as_view(), name='favorite_delete'),
]
