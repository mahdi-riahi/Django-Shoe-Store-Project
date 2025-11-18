from django.shortcuts import render
from django.views import generic
from django.utils import timezone

from datetime import timedelta

from products.models import Product


def home_page_view(request):
    # High sell products
    best_selling_products = Product.objects.all().order_by('-sell_count', '-is_active', )[:8]

    # New products (last 2 weeks)
    two_weeks_ago = timezone.now() - timedelta(days=14)
    new_products = Product.objects.filter(
        is_active=True,
        datetime_created__gte=two_weeks_ago
    ).order_by('-datetime_created')[:8]

    # Offer products
    discounted_products = Product.objects.filter(
        is_active=True,
        offer=True
    )[:8]

    # Products Based on major category
    women_products = Product.objects.filter(
        major_category='Women'
    ).order_by('-is_active')[:6]

    men_products = Product.objects.filter(
        major_category='Men'
    ).order_by('-is_active')[:6]

    bags_products = Product.objects.filter(
        major_category='Bags'
    ).order_by('-is_active')[:6]

    clothing_products = Product.objects.filter(
        major_category='Clothing'
    ).order_by('-is_active')[:6]

    context = {
        'best_selling_products': best_selling_products,
        'new_products': new_products,
        'discounted_products': discounted_products,
        'women_products': women_products,
        'men_products': men_products,
        'bags_products': bags_products,
        'clothing_products': clothing_products,
    }

    return render(request, 'home_page.html', context)

class AboutPageView(generic.TemplateView):
    template_name = 'pages/about_page.html'


class ContactPageView(generic.TemplateView):
    template_name = 'pages/contact_page.html'
