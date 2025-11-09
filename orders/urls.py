from django.urls import path

from . import views


app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create_view, name='order_create'),
    path('', views.OrderListView.as_view(), name='order_list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/update/', views.OrderUpdateView.as_view(), name='order_update'),
    path('<int:pk>/confirm/', views.order_confirm_view, name='order_confirm'),
]
