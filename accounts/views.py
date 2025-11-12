from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.contrib import messages
from django.contrib.auth import get_user_model, login, authenticate
from django.core.mail import send_mail

from .models import PhoneVerification
from .forms import CustomUserCreationForm, PhoneVerificationForm, LoginForm
from .sms_service import SMSService


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            verification = PhoneVerification.objects.create(
                phone_number=user.phone_number,
            )

            SMSService.send_verification_code(user.phone_number, verification.code)

            # Mark session
            # request.session['phone_number_for_verification'] = user.phone_number
            request.session['user_id'] = str(user.id)

            messages.success(request, _('Please confirm your phone number'))
            return redirect('accounts:verify_phone')

        messages.error(request, _('Please correct errors below'))

    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})


def verify_phone_view(request):
    # Check session for user_id
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, _('Please complete signup first'))
        return redirect('accounts:signup')

    User = get_user_model()
    # Get user
    try:
        user = User.objects.get(id=int(user_id))

    except User.DoesNotExist:
        messages.error(request, _('Signup is incomplete. Please complete signup first'))
        return redirect('accounts:signup')

    if request.method == 'POST':
        form = PhoneVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']

            try:
                # Get verification obj if existed
                verification = PhoneVerification.objects.get(
                    phone_number=user.phone_number,
                    code=code,
                    is_used=False,
                )
                # Check if verification is valid
                if verification.is_valid():
                    # Mark all existing verifications as used
                    PhoneVerification.objects.filter(
                        phone_number=user.phone_number,
                        is_used=False,
                    ).update(is_used=True)

                    # Update user is_active, phone_verified
                    user.phone_verified = True
                    user.is_active = True
                    user.save()

                    # Send Welcome Email
                    send_mail(
                        'Welcome to Our Shop',
                        'Thank you for registering!',
                        'noreply@jcclassic.com',
                        [user.email],
                        fail_silently=False,
                    )

                    # Cleanup session
                    del request.session['user_id']

                    # Log the user in
                    login(request, user)

                    messages.success(request, _('Phone number validation was successful. Signup completed'
                                                '\nYou are logged in now'))
                    # Redirect to home
                    return redirect('pages:home_page')

                else:
                    messages.error(request, _('Code is expired. Please ask for a new code'))

            except PhoneVerification.DoesNotExist:
                messages.error(request, _('code is not valid.'))

        else:
            messages.error(request, _('No verification code sent'))

    else:
        form = PhoneVerificationForm()

    return render(request, 'accounts/verify_phone.html', {
        'phone_number': user.phone_number,
        'form': form,
    })


def resend_verification_code_view(request):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, _('Please complete signup first'))
        return redirect('accounts:signup')

    User = get_user_model()
    try:
        user = User.objects.get(id=int(user_id))

    except User.DoesNotExist:
        messages.error(request, _('Signup is incomplete. Please complete signup first'))
        return redirect('accounts:signup')

    try:
        # Check if there is unused verifications
        verification = PhoneVerification.objects.filter(
            phone_number=user.phone_number,
            is_used=False,
        ).latest('datetime_created')

        # Redirect to verify_phone if verification is valid
        if verification.is_valid():
            messages.info(request, _('Your last code is still valid. Use that or wait until it get expired and try again'))
            return redirect('accounts:verify_phone')

    except PhoneVerification.DoesNotExist:
        # If there is no verification, we move on to create a new one
        pass

    # Mark all existing verifications as used
    PhoneVerification.objects.filter(
        phone_number=user.phone_number,
        is_used=False,
    ).update(is_used=True)

    # Create a new verification code
    new_verification = PhoneVerification.objects.create(
        phone_number=user.phone_number,
    )

    # Send sms
    SMSService.send_verification_code(user.phone_number, new_verification.code)

    messages.success(request, _('Verification code sent successfully.'))
    return redirect('accounts:verify_phone')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email_or_phone = form.cleaned_data['email_or_phone']
            password = form.cleaned_data['password']

            # Check if email was entered
            if '@' in email_or_phone and '.' in email_or_phone:
                # Authenticate with email and password
                user = authenticate(request, email=email_or_phone, password=password)

            # If phone was entered
            else:
                User = get_user_model()
                try:
                    # Find user object and its email
                    user_obj = User.objects.get(phone_number=email_or_phone)
                    #Authenticate with email and password
                    user = authenticate(request, email=user_obj.email, password=password)

                except User.DoesNotExist:
                    user = None

            # If user is authenticated
            if user is not None:
                # Check if user phone_verified is True
                if user.phone_verified:
                    # Log the user in
                    login(request, user)
                    messages.success(request, _(f'You are logged in as {user.phone_number}'))
                    return redirect('pages:home_page')

                # Redirect to verify_phone because user phone_verified is False
                else:
                    messages.warning(request, _('You have to verify your phone number first and then log in'))
                    request.session['user_id'] = str(user.id)
                    return redirect('accounts:verify_phone')

        # User not found
        else:
            messages.error(request, _('Email or phone number or password invalid'))
            form.add_error(None, _('Email/Phone number/Password is invalid'))

    # Request method is 'GET'
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})
