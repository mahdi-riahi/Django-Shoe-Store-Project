from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotFound
from django.views import generic
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator

from .models import Product, Comment
from .forms import CommentForm


class ProductListView(generic.ListView):
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 10
    queryset = Product.active_product_manager.all()

    # Product.objects.filter(variants__size=42) I'm gonna use it later

    def get_queryset(self):
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

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data()
        context['comment_form'] = CommentForm()

        comments = self.object.comments.filter(is_active=True).order_by('-datetime_modified')

        paginator = Paginator(comments, 10)
        page_number = self.request.GET.get('page')
        comment_page_obj = paginator.get_page(page_number)
        context['comments_page_obj'] = comment_page_obj
        context['comments_num_pages'] = paginator.num_pages
        return context


def product_major_category_list_view(request, major_category):
    if major_category not in Product.get_major_categories_list():
        return HttpResponseNotFound('Page not found')
    categories = Product.get_categories_from_major_cat(major_category)
    query_dict = {category: Product.active_product_manager.filter(category=category)[:5] for category in categories}
    return render(
        request,
        'products/major_category_product_list.html',
        {'query_dict': query_dict, 'major_category': major_category}
    )


def product_category_list_view(request, major_category, category):
    if any([
        major_category not in Product.get_major_categories_list(),
        category not in Product.get_categories_from_major_cat(major_category),]):
        return HttpResponseNotFound('Page not found')
    products = Product.active_product_manager.filter(category=category)
    return render(request,'products/category_product_list.html', {
        'products': products,
        'category':category,
        'major_category': major_category,
    })
    # Remember to add pagination to this view. other list views don't need pagination.


@method_decorator(require_http_methods(["POST", ]), name='dispatch')
class CommentCreateView(generic.CreateView):
    model = Comment
    form_class = CommentForm

    def get_success_url(self):
        return reverse_lazy('products:product_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        product = get_object_or_404(Product, pk=int(self.kwargs['pk']))
        comment = form.save(commit=False)
        comment.product = product
        user = self.request.user
        if user.is_authenticated:
            comment.user = user
            comment.name = user.username
            comment.email = user.email
        else:
            cleaned_data = form.cleaned_data
            print(cleaned_data)
            comment.name = cleaned_data.get('name', )
            comment.email = cleaned_data.get('email', )
            print(comment.name, comment.email)
        comment.save()
        print('saved!')

        messages.success(self.request, _('Your comment added successfully'))
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, _('Please correct the errors for comment.'))
        return redirect(self.get_success_url())
