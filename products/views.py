from django.shortcuts import render
from django.views import generic

from .models import Product


class ProductListView(generic.ListView):
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 10
    queryset = Product.active_product_manager.all()
    # Product.objects.filter(shoes_variants__size=42) I'm gonna use it later

    def get_queryset(self) :
        return Product.active_product_manager.all()


    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context['women_shoes'] = Product.active_product_manager.filter(major_category='Women')[:5]
        context['men_shoes'] = Product.active_product_manager.filter(major_category='Men')[:5]
        context['bags'] = Product.active_product_manager.filter(major_category='Bags')[:5]
        context['clothing'] = Product.active_product_manager.filter(major_category='Clothing')[:5]
        context['accessory'] = Product.active_product_manager.filter(major_category='Accessory')[:5]
        context['shoescare'] = Product.active_product_manager.filter(major_category='ShoesCare')[:5]
        return context


class ProductDetailView(generic.DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'products/product_detail.html'
