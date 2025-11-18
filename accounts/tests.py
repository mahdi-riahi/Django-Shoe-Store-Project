from django.test import TestCase
from django.shortcuts import reverse
import time

from .models import CustomUser, PhoneVerification

# Running this test takes 2 minutes
class PhoneVerificationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.phone_number='09131234567'
        PhoneVerification.objects.create(
            phone_number=cls.phone_number,
        )

    def test_phone_verification_object(self):
        # Check object existence
        self.assertTrue(PhoneVerification.objects.exists())

        verification = PhoneVerification.objects.last()
        # Check object attrs
        self.assertEqual(verification.phone_number, self.phone_number)
        self.assertEqual(len(verification.code), 6)

        # Check magic methods
        self.assertEqual(str(verification), self.phone_number.replace('0', '+98'))

        # Check object methods
        self.assertTrue(verification.is_valid())

        # This last one is not necessary because takes 2 minutes to be completed
        # Wait for 2 min and check object validation
        time.sleep(121)
        self.assertFalse(verification.is_valid())


class CustomUserTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            'email': '123@gmail.com',
            'phone_number': '09123456789',
            'username': 'test_username',
            'password': '1234567890',
        }
        cls.user = CustomUser.objects.create_user(
            email=cls.user_data['email'],
            phone_number=cls.user_data['phone_number'],
            username=cls.user_data['username'],
        )

    def test_user_object(self):
        # Get object
        user = CustomUser.objects.last()
        # Check object attrs
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.phone_number, self.user_data['phone_number'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertFalse(user.phone_verified)
        self.assertFalse(user.email_verified)

        # Check object methods
        self.assertEqual(str(user), self.user_data['email'])
        self.assertEqual(user.get_absolute_url(), reverse('profile:profile_detail'))


class SignupTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            'email': '123@gmail.com',
            'phone_number': '09123456789',
            'username': 'test_username',
            'password': 'afjlk8i43frejioJD',
        }

    def test_signup_get_url_and_url_by_name(self):
        response1 = self.client.get('/accounts/signup/')
        self.assertEqual(response1.status_code, 200)

        response2 = self.client.get(reverse('accounts:signup'))
        self.assertEqual(response2.status_code, 200)

        # Check elements in response
        self.assertContains(response1, 'form')
        self.assertContains(response1, 'Signup')
        self.assertTemplateUsed(response1, 'accounts/signup.html')

    def test_signup_post_valid(self):
        """
        Successful Signup
        """
        response1 =  self.client.post(reverse('accounts:signup'), {
            'email': self.user_data['email'],
            'phone_number': self.user_data['phone_number'],
            'password1': self.user_data['password'],
            'password2': self.user_data['password'],
        })

        self.assertEqual(response1.status_code, 302)
        self.assertRedirects(response1, reverse('accounts:verify_phone'))

        # Check if user is created
        self.assertTrue(CustomUser.objects.filter(email=self.user_data['email']).exists())
        user = CustomUser.objects.get(email=self.user_data['email'])

        # Check if user is active & verified
        self.assertFalse(user.phone_verified)
        self.assertFalse(user.is_active)

        # Check if phone_verification object is created
        self.assertTrue(PhoneVerification.objects.filter(phone_number=self.user_data['phone_number']).exists())
        verification = PhoneVerification.objects.get(phone_number=self.user_data['phone_number'])

        # Ask for a new code (should not receive a new code)
        response2 = self.client.get(reverse('accounts:resend_code'))
        # Check if new verification code is created
        count = PhoneVerification.objects.filter(phone_number=self.user_data['phone_number']).count()
        self.assertEqual(count, 1)

        # Send verification code to phone_verify_view
        response3 = self.client.post(reverse('accounts:verify_phone'), {
            'code': verification.code,
        })
        # Check if user is logged in
        self.assertEqual(response3.status_code, 302)
        self.assertRedirects(response3, reverse('pages:home_page'))
        # Check user's active and phone_verified
        self.assertTrue(user.is_authenticated)
        print(f'user is logged in: {user.is_authenticated}')
        self.assertTrue(user.phone_verified)
        self.assertTrue(user.is_active)
