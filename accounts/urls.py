from django.urls import path

from . import views


app_name = 'user'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/change/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('favorites/', views.FavoriteListView.as_view(), name='favorite_list'),
]
