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
        cls.product_data = {
            'title': 'title',
            'description': 'description',
            'price': 1450000,
            'short_description': 'Short description',
            'category': 'shoulder-bags',
        }
        cls.product = Product.objects.create(
            title=cls.product_data['title'],
            short_description=cls.product_data['short_description'],
            description=cls.product_data['description'],
            price=cls.product_data['price'],
            category=cls.product_data['category'],
            user=cls.user,
        )

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
        self.assertContains(response, self.product_data['title'])
        self.assertContains(response, self.product_data['short_description'])
        # self.assertContains(response, '۱۴۵۰۰۰۰')

    def test_home_page_url_by_name(self):
        response = self.client.get(reverse('pages:home_page'))
        self.assertEqual(response.status_code, 200)

    def test_about_page_url(self):
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)

    def test_about_page_url_by_name(self):
        response = self.client.get(reverse('pages:about_page'))
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'pages/about_page.html')

        self.assertContains(response, "This is About-Us page")

    def test_contact_page_url(self):
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)

    def test_contact_page_url_by_name(self):
        response = self.client.get(reverse('pages:contact_page'))
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'pages/contact_page.html')

        self.assertContains(response, "Address")
        self.assertContains(response, 'Kurosh St.')
        self.assertContains(response, 'Iran, Isfahan')
        self.assertContains(response, 'form')
