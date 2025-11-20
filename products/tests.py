from django.test import TestCase
from django.contrib.auth import get_user_model, login
from django.urls import reverse

from .models import Product, ProductVariant, Cover, Comment


User = get_user_model()

class ProductTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='test@test.com',
            phone_number='09123456789',
        )
        cls.product_data = {
            'title': 'Title',
            'short_description': 'This is Short Description',
            'description': 'This is Product Description',
            'category': 'm-summer',
            'get_category_display': 'Men Summer Shoes',
            'major_category': 'Men',
            'invalid_major_category': 'Bags',
            'price': 6500000,
            'offer_price': 5200000,
            'invalid_offer_price': 8500000,
            'offer_percent': 20,
        }
        cls.product = Product.objects.create(
            title=cls.product_data['title'],
            short_description=cls.product_data['short_description'],
            description=cls.product_data['description'],
            category=cls.product_data['category'],
            # Test if model can find valid major_category before saving
            major_category=cls.product_data['invalid_major_category'],
            price=cls.product_data['price'],
            user=cls.user,
        )

    def test_product_creation(self):
        """
        Check product creation and different elements
        """
        self.assertEqual(self.product.title, self.product_data['title'])
        self.assertEqual(self.product.short_description, self.product_data['short_description'])
        self.assertEqual(self.product.description, self.product_data['description'])
        self.assertEqual(self.product.category, self.product_data['category'])
        self.assertEqual(self.product.get_category_display(), self.product_data['get_category_display'])
        self.assertEqual(self.product.price, self.product_data['price'])
        self.assertEqual(self.product.offer_price, self.product.price)
        self.assertFalse(self.product.offer)
        self.assertEqual(self.product.sell_count, 0)
        self.assertFalse(self.product.is_active)
        # Test __str__ magic method
        self.assertEqual(str(self.product), self.product_data['title'])
        # Test get_absolute_url()
        url = reverse('products:product_detail', kwargs={'pk': self.product.pk})
        self.assertEqual(self.product.get_absolute_url(), url)

    def test_product_methods(self):
        """
        Test product object methods (not related to other models)
        """
        # Test get_major_category
        self.assertEqual(self.product.get_major_category(), self.product_data['major_category'])

        # Test get_offer_percent
        self.assertEqual(self.product.get_offer_percent(), 0)
        # Change offer price and test again
        self.product.offer = True
        self.product.offer_price = self.product_data['offer_price']
        self.product.save()
        self.assertEqual(self.product.get_offer_percent(), self.product_data['offer_percent'])

    def test_class_methods(self):
        """
        Test Product class methods regardless of instance
        """
        categories_in_major_cat = {
            'm-summer': 'Men Summer Shoes',
            'm-sport': 'Men Sport Shoes',
            'm-medical': 'Men Medical Shoes',
            'm-formal': 'Men Formal Shoes',
            'm-occasional': 'Men Occasional Shoes',
            'm-winter': 'Men Winter Shoes',
        }
        major_categories_list = ['Women', 'Men', 'Bags', 'Clothing', 'Accessory', 'ShoesCare']
        categories_list = [
            'w-summer', 'w-casual', 'w-sport', 'w-medical', 'w-formal', 'w-heels', 'w-winter',
            'm-summer', 'm-sport', 'm-medical', 'm-formal', 'm-occasional', 'm-winter',
            'hand-bag', 'shoulder-bags', 'office-bag', 'travel-bag', 'back-pack', 'card-holder', 'coat-bag', 'checkbook-bag',
            'm-jackets', 'w-jackets', 'hats',
            'm-accessories', 'w-accessories',
            'medical-insole', 'wax',
        ]
        # Test get_categories_from_major_cat
        self.assertEqual(Product.get_categories_from_major_cat(self.product.major_category), categories_in_major_cat)
        # Test get_major_categories_list
        self.assertEqual(Product.get_major_categories_list(), major_categories_list)
        # Test get_categories_list
        self.assertEqual(Product.get_categories_list(), categories_list)
        # Test find_category_display_from_category
        self.assertEqual(
            Product.find_category_display_from_category(self.product.category),
            self.product_data['get_category_display']
        )
        # Test find_category_from_category_display
        self.assertEqual(
            Product.find_category_from_category_display(self.product_data['get_category_display']),
            self.product.category
        )


class ProductVariantTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='test@test.com',
            phone_number='09123456789',
        )
        cls.product1 = Product.objects.create(
            title='TestTitle1',
            short_description='Test Short description1',
            description='TestProductDescription1',
            category='w-jackets',
            price=4560000,
            user=cls.user,
        )
        cls.product2 = Product.objects.create(
            title='TestTitle2',
            short_description='Test Short description2',
            description='TestProductDescription2',
            category='wax',
            price=128000,
            user=cls.user,
        )
        cls.variant = ProductVariant.objects.create(
            product=cls.product1,
            quantity=2,
            color='gr',
            size=38,
        )

    def test_product_active_product_manager(self):
        """
        Test custom product managers: with creating a variant related to product, product becomes active
        """
        active_products = Product.active_product_manager.all()
        # product1 -> active
        # product2 -> inactive
        self.assertIn(self.product1, active_products)
        self.assertNotIn(self.product2, active_products)

    def test_variant_creation(self):
        """
        Test variant object attrs and magic methods
        """
        self.assertEqual(self.variant.product, self.product1)
        self.assertEqual(self.variant.quantity, 2)
        self.assertEqual(self.variant.color, 'gr')
        self.assertEqual(self.variant.size, 38)
        # test str method
        variant_string = (
            f'{self.variant.product.title} -'
            f' Color: {self.variant.get_color_display()} -'
            f' Size: {self.variant.size}'
        )
        self.assertEqual(str(self.variant), variant_string)

    def test_variant_save_no_quantity(self):
        """
        Decrease quantity to 0 and check if variant and product's is_active are updated to False
        """
        self.variant.quantity = 0
        self.variant.save()
        self.assertFalse(self.variant.is_active)
        self.assertFalse(self.product1.is_active)

    def test_variant_is_available(self):
        """
        Test is_available method with different amounts
        """
        # Lower than existing quantity
        self.assertTrue(self.variant.is_available(1))
        self.assertFalse(self.variant.is_available(3))

    def test_variant_decrease_and_increase_quantity(self):
        """
        Test decrease and increase quantities
        """
        # Decrease quantity to 0 and deactivate the variant
        self.variant.decrease_quantity(2)
        quantity1 = self.variant.quantity
        # Try to decrease more
        self.variant.decrease_quantity(1)
        quantity2 = self.variant.quantity
        # Check if quantity still equals 0
        self.assertEqual(quantity1, 0)
        self.assertEqual(quantity1, quantity2)

        # Increase quantity and activate it
        self.variant.increase_quantity(1)
        self.assertEqual(self.variant.quantity, 1)
        # Check if variant is activated
        self.assertTrue(self.variant.is_active)


class CommentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            phone_number='09123456789',
        )
        self.product = Product.objects.create(
            title='TestTitle',
            short_description='Test Short description',
            description='TestProductDescription',
            category='w-jackets',
            price=4560000,
            user=self.user,
        )
        self.comment = Comment.objects.create(
            text='test comment',
            product = self.product,
        )
    def test_comment_creation(self):
        """
        Test comment attrs and methods
        """
        self.assertEqual(self.comment.product, self.product)
        self.assertEqual(self.comment.text, 'test comment')
        self.assertTrue(self.comment.recommend)
        self.assertTrue(self.comment.is_active)

        self.assertEqual(str(self.comment), f'{self.product} - {self.comment.rate}')

        url = reverse('products:product_detail', kwargs={'pk': self.product.pk})
        self.assertEqual(self.comment.get_absolute_url(), url)


class CoverTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            phone_number='09123456789',
        )
        self.product = Product.objects.create(
            title='TestTitle',
            short_description='Test Short description',
            description='TestProductDescription',
            category='w-jackets',
            price=4560000,
            user=self.user,
        )

    def test_cover_creation(self):
        """
        Test cover object attrs and str magic method
        """
        self.cover = Cover.objects.create(
            product=self.product,
            cover='products/covers/test_cover.jpg',
        )
        self.assertEqual(self.cover.product, self.product)
        self.assertEqual(self.cover.cover, 'products/covers/test_cover.jpg')
        self.assertEqual(str(self.cover), str(self.product))


class ProductListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='test@test.com',
            phone_number='09123456789',
        )
        cls.product1 = Product.objects.create(
            title='Loafer 320 Sport',
            short_description='The newest 2026 sport model',
            description='Men sport TestDescription',
            category='m-sport',
            price=4560000,
            user=cls.user,
        )
        cls.product2 = Product.objects.create(
            title='Women long winter jacket code 527',
            short_description='The Warmest leather coat',
            description='Women jackets TestDescription',
            category='w-jackets',
            price=13700000,
            offer=True,
            offer_price=9800000,
            user=cls.user,
        )

    def test_product_list_view_get_url_and_url_by_name(self):
        """
        Test GET request by url or name
        """
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, 200)
        # Check templates used
        self.assertTemplateUsed(response, 'products/product_list.html')
        self.assertTemplateUsed(response, 'products/partials/product_card.html')
        # Check elements in page
        self.assertContains(response, 'Complete Collection')
        self.assertContains(response, 'Browse our products by your favorite categories')
        # Check context in the response
        self.assertIn('query_dict', response.context)
        self.assertIn('products', response.context)
        # Check products details in page
        self.assertContains(response, self.product1.title)
        self.assertContains(response, self.product2.title)
        self.assertContains(response, self.product1.short_description)
        self.assertContains(response, self.product2.short_description)


class ProductDetailView(TestCase):
    @classmethod
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            phone_number='09123456789',
        )
        self.product = Product.objects.create(
            title='Loafer 320 Sport',
            short_description='The newest 2026 sport model',
            description='Men sport TestDescription',
            category='m-sport',
            price=4560000,
            user=self.user,
        )
        self.active_variant = ProductVariant.objects.create(
            product=self.product,
            quantity=3,
            size=41,
            color='bk',
        )
        self.inactive_variant = ProductVariant.objects.create(
            product=self.product,
            quantity=0,
            size=44,
            color='ce',
        )
        self.comment = Comment.objects.create(
            name='Test author',
            text='Test Comment',
            product=self.product,
        )
        self.response = self.client.get(reverse('products:product_detail', kwargs={'pk': self.product.pk}))

    def test_product_detail_get_url(self):
        """
        Test GET request by url
        """
        # url
        response = self.client.get(f'/products/{self.product.pk}/')
        self.assertEqual(response.status_code, 200)
        # Check templates used
        self.assertTemplateUsed(response, 'products/product_detail.html')
        self.assertTemplateUsed(response, 'products/category_navbar.html')
        self.assertTemplateUsed(response, '_base.html')
        # Check elements in page
        self.assertContains(response, 'Details for')
        self.assertContains(response, 'Material')
        self.assertContains(response, 'Sizes')
        self.assertContains(response, 'Comments')
        self.assertContains(response, 'form')
        # Check context in the response
        self.assertIn('comment_form', response.context)
        self.assertIn('comments_page_obj', response.context)
        self.assertIn('comments_num_pages', response.context)
        self.assertIn('color_form_dict', response.context)

    def test_product_detail_get_url_by_name(self):
        """
        Test GET url by name
        """
        self.assertEqual(self.response.status_code, 200)

    def test_product_and_variant_detail(self):
        """
        Test Product details and product's active variants
        """
        # Check products details in page
        self.assertContains(self.response, self.product.title)
        self.assertContains(self.response, self.product.short_description)
        self.assertContains(self.response, self.product.description)
        # Check active variant
        self.assertContains(self.response, self.active_variant.get_color_display())
        self.assertContains(self.response, self.active_variant.get_size_display())
        # Check inactive variant
        self.assertNotContains(self.response, self.inactive_variant.get_color_display())
        self.assertNotContains(self.response, self.inactive_variant.get_size_display())

    def test_comment_detail(self):
        self.assertContains(self.response, self.comment.text)
        self.assertContains(self.response, self.comment.name)


class CommentCreateView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='test@test.com',
            phone_number='09123456789',
            is_active=True,
            phone_verified=True,
            password='859rfiok85erfj',
        )
        cls.product = Product.objects.create(
            title='Loafer 320 Sport',
            short_description='The newest 2026 sport model',
            description='Men sport TestDescription',
            category='m-sport',
            price=4560000,
            user=cls.user,
        )

    def test_comment_create_anonymous_valid(self):
        """
        Test comment creation as anonymous
        """
        self.client.post(reverse('products:comment_create', kwargs={'pk': self.product.pk}), {
            'name': 'Test Name',
            'email': '123@gmail.com',
            'text': 'Some text',
            'recommend': False,
        })
        # Check if comment is created
        self.assertEqual(Comment.objects.last().name, 'Test Name')
        self.assertEqual(Comment.objects.last().email, '123@gmail.com')
        self.assertEqual(Comment.objects.last().text, 'Some text')
        self.assertEqual(Comment.objects.last().recommend, False)

    def test_comment_create_anonymous_invalid(self):
        """
        Test comment creation with invalid data
        """
        self.client.post(reverse('products:comment_create', kwargs={'pk': self.product.pk}), {
            'text': 'Test text',
            'recommend': False,
        })
        self.assertEqual(Comment.objects.last().text, 'Test text')

    def test_comment_create_authenticated(self):
        """
        Test comment creation as authenticated user
        """
        # Log the user in (user gets authenticated)
        response = self.client.post(reverse('accounts:login'), {
            'email_or_phone': self.user.phone_number,
            'password': '859rfiok85erfj',
        })


        # Send post request to create a new comment
        self.client.post(reverse('products:comment_create', kwargs={'pk': self.product.pk}), {
            'text': 'Authenticated text',
            'recommend': True,
        })
        # Check comment creation
        comment = Comment.objects.last()
        self.assertEqual(comment.text, 'Authenticated text')
        self.assertEqual(comment.recommend, True)
        self.assertEqual(comment.name, self.user.username)
        self.assertEqual(comment.email, self.user.email)
