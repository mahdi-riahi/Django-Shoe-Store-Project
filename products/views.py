from django.shortcuts import render
from django.views import generic

from .models import Product


class ProductListView(generic.ListView):
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 10
    queryset = Product.active_product_manager.all()


class ProductDetailView(generic.DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'products/product_detail.html'
