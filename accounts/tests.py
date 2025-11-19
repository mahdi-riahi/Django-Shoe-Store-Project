from django.test import TestCase
from django.shortcuts import reverse
import time

from .models import CustomUser, PhoneVerification
from .forms import CustomUserCreationForm


# Running this test takes 2 minutes
class PhoneVerificationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.phone_number='09131234567'
        PhoneVerification.objects.create(
            phone_number=cls.phone_number,
        )

    def test_phone_verification_object(self):
        """
        Check verification object's existence and attrs
        """
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
        """
        Check if user is created and have attrs as expected
        """
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
            'invalid_password': '9fjisod9090ir',
        }

    def test_signup_get_url_and_url_by_name(self):
        """
        Get signup url and check the elements
        """
        response1 = self.client.get('/accounts/signup/')
        self.assertEqual(response1.status_code, 200)

        response2 = self.client.get(reverse('accounts:signup'))
        self.assertEqual(response2.status_code, 200)

        # Check elements in response
        self.assertContains(response1, 'form')
        self.assertContains(response1, 'Signup')
        self.assertTemplateUsed(response1, 'accounts/signup.html')

    # Test fails because in the end user is_active and phone_verified is false
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

        # Check verify_phone (get) url, url by name
        response2 = self.client.get('/accounts/verify_phone/')
        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, 'accounts/verify_phone.html')
        self.assertContains(response2, 'form')
        response3 = self.client.get(reverse('accounts:verify_phone'))
        self.assertEqual(response3.status_code, 200)

        # Check if user is active & verified
        self.assertFalse(user.phone_verified)
        self.assertFalse(user.is_active)

        # Check if phone_verification object is created
        self.assertTrue(PhoneVerification.objects.filter(phone_number=self.user_data['phone_number']).exists())
        verification = PhoneVerification.objects.get(phone_number=self.user_data['phone_number'])

        # Ask for a new code (should not receive a new code)
        response4 = self.client.get(reverse('accounts:resend_code'))
        # Check if new verification code is created
        count = PhoneVerification.objects.filter(phone_number=self.user_data['phone_number']).count()
        self.assertEqual(count, 1)

        # Send verification code to phone_verify_view
        response5 = self.client.post(reverse('accounts:verify_phone'), {
            'code': verification.code,
        })
        # Check if user is logged in
        self.assertEqual(response5.status_code, 302)
        self.assertRedirects(response5, reverse('pages:home_page'))
        # Check user's active and phone_verified
        self.assertTrue(user.is_authenticated)
        user.refresh_from_db()
        self.assertTrue(user.phone_verified)
        self.assertTrue(user.is_active)

        # Get verify_phone, resend_code, signup, login while we are logged in
        response = self.client.get(reverse('accounts:signup'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('accounts:verify_phone'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('accounts:resend_code'))
        self.assertEqual(response.status_code, 302)

    def test_signup_post_not_valid(self):
        """
        Unsuccessful signup
        """
        response1 =  self.client.post(reverse('accounts:signup'), {
            'email': self.user_data['email'],
            'phone_number': self.user_data['phone_number'],
            'password1': self.user_data['password'],
            'password2': self.user_data['invalid_password'],
        })
        self.assertEqual(response1.status_code, 200)
        # Check if verification code is created
        self.assertFalse(PhoneVerification.objects.filter(phone_number=self.user_data['phone_number']).exists())
        # Check if user is created
        self.assertFalse(CustomUser.objects.filter(email=self.user_data['email']).exists())

        # Get verify_phone, resend_code views
        response2 = self.client.get(reverse('accounts:verify_phone'))
        self.assertEqual(response2.status_code, 302)
        self.assertRedirects(response2, reverse('accounts:signup'))

        response3 = self.client.get(reverse('accounts:resend_code'))
        self.assertEqual(response3.status_code, 302)
        self.assertRedirects(response3, reverse('accounts:signup'))


class LoginTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            'email': '123@gmail.com',
            'phone_number': '09123456789',
            'username': 'test_username',
            'password1': 'afjlk8i43frejioJD',
            'password2': '0u9ewids9)Ih88',
        }
        cls.user = CustomUser.objects.create_user(
            email = cls.user_data['email'],
            phone_number = cls.user_data['phone_number'],
            username = cls.user_data['username'],
            password = cls.user_data['password1'],
            phone_verified=True,
        )

    def test_login_get_url_and_url_by_name(self):
        """
        Get login url and check the elements
        """
        response1 = self.client.get('/accounts/login/')
        self.assertEqual(response1.status_code, 200)

        response2 = self.client.get(reverse('accounts:login'))
        self.assertEqual(response2.status_code, 200)

        # Check elements of response
        self.assertTemplateUsed(response2, 'accounts/login.html')
        self.assertContains(response2, 'form')
        self.assertContains(response2, 'Login')

    def test_login_post_invalid(self):
        """
        Unsuccessful login with invalid information
        """
        # Invalid password
        response = self.client.post(reverse('accounts:login'), {
            'email_or_phone': self.user_data['email'],
            'password': self.user_data['password2'],
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        # Invalid email/username
        response = self.client.post(reverse('accounts:login'), {
            'email_or_phone': '09877158821',
            'password': self.user_data['password1'],
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_successful_with_email(self):
        """
        Successful login with email
        """
        response = self.client.post(reverse('accounts:login'), {
            'email_or_phone': self.user_data['email'],
            'password': self.user_data['password1'],
        })
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertRedirects(response, reverse('pages:home_page'))

    def test_login_successful_with_phone_number(self):
        """
        Successful login with phone_number
        """
        response = self.client.post(reverse('accounts:login'), {
            'email_or_phone': self.user_data['phone_number'],
            'password': self.user_data['password1'],
        })
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertRedirects(response, reverse('pages:home_page'))

    def test_login_post_valid_phone_not_verified(self):
        # Mark user as phone not verified
        self.user.phone_verified = False
        self.user.save()

        response = self.client.post(reverse('accounts:login'), {
            'email_or_phone': self.user_data['phone_number'],
            'password': self.user_data['password1'],
        })
        # Check if redirects to phone_verify
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:verify_phone'))

        # Ask to resend code
        response = self.client.get(reverse('accounts:resend_code'))
        self.assertRedirects(response, reverse('accounts:verify_phone'))

        # Check if a new code is created
        self.assertTrue(PhoneVerification.objects.filter(phone_number=self.user_data['phone_number']).exists())

        # Use the new code to verify phone number
        verification = PhoneVerification.objects.filter(phone_number=self.user_data['phone_number']).latest('datetime_created')
        response = self.client.post(reverse('accounts:verify_phone'), {
            'code': verification.code,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('pages:home_page'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        # Check user phone_verified
        self.user.refresh_from_db()
        self.assertTrue(self.user.phone_verified)


class SignupFormTest(TestCase):
    def test_valid_signup_form(self):
        form_data = {
            'email': '123@gmail.com',
            'phone_number': '+989123456789',
            'password1': 'first_password1',
            'password2': 'first_password1',
        }
        form = CustomUserCreationForm(form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_signup_form(self):
        form_data = {
            'email': '123@gmail.com',
            'phone_number': '+849123456789',
            'password1': 'first_password1',
            'password2': 'second_password2',
        }
        form = CustomUserCreationForm(form_data)
        self.assertFalse(form.is_valid())

    def test_duplicate_email_signup_form(self):
        """
        Test Signup with duplicate email
        """
        form_data1 = {
            'email': '123@gmail.com',
            'phone_number': '09123456789',
            'password1': 'first_password1',
            'password2': 'first_password1',
        }
        form1 = CustomUserCreationForm(form_data1)
        form1.save()

        form_data2 = {
            'email': '123@gmail.com',
            'phone_number': '09123456777',
            'password1': 'first_password1',
            'password2': 'first_password1',
        }
        form2 = CustomUserCreationForm(form_data2)
        self.assertFalse(form2.is_valid())
        self.assertIn('email', form2.errors)
