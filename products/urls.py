from django.urls import path

from .import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('<str:major_category>/', views.product_major_category_list_view, name='product_major_cat_list'),
    path('<str:major_category>/<str:category>/', views.product_category_list_view, name='product_category_list'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('<int:pk>/comment_add/', views.CommentCreateView.as_view(), name='comment_create'),
]
