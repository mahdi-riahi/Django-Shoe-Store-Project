from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Product, ProductVariant, Cover, Comment


User = get_user_model()

class ProductTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='test@test.com',
            phone_number='09123456789',
        )
        cls.product = Product.objects.create(
            title='Title',
            short_description='This is Short Description',
            description='This is Product Description',
            category='m-summer',
            price=6860000,
            user=cls.user,
        )
