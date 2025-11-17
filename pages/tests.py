from django.test import TestCase
from django.shortcuts import reverse

from products.models import Product
from accounts.models import CustomUser


class PagesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            email='user@email.com',
            phone_number='09131451541',
            username='user',
        )
        cls.product = Product.objects.create(
            title='Title',
            short_description='Short description',
            description='Description',
            price=1450000,
            category='shoulder-bags',
            user=cls.user,
        )
    # Failed (product isn't there)
    def test_home_page_url(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Check template used
        self.assertTemplateUsed(response, 'home_page.html')
        self.assertTemplateUsed(response, 'cart/mini_cart_aside.html')
        self.assertTemplateUsed(response, '_base.html')
        self.assertTemplateUsed(response, 'products/category_navbar.html')
        self.assertTemplateUsed(response, 'products/partials/product_card.html')
        # Check Text in page
        self.assertContains(response, 'Welcome to the World of Fashion and Beauty')
        self.assertContains(response, 'For purchases over 500,000 Tomans')
        # Check product info
        self.assertContains(response, 'Title')
        self.assertContains(response, 'Short description')
        self.assertContains(response, '۱۴۵۰۰۰۰')

    def test_home_page_url_by_name(self):
        response = self.client.get(reverse('pages:home_page'))
        self.assertEqual(response.status_code, 200)
