from django.urls import path

from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail_view, name='cart_detail'),
    path('add/<int:variant_id>/', views.cart_add_update_view, name='cart_add'),
    path('remove/<int:product_id>', views.cart_remove_product_view, name='cart_remove'),
    path('clear/', views.cart_clear_view, name='cart_clear'),
]
