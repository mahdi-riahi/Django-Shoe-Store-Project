from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
import random

from .sms_service import send_sms_verification
from accounts.models import PhoneVerification

@login_required
def verify_phone(request):
    if request.method == 'POST':
        entered_code = request.POST.get('code')

        try:
            verification = PhoneVerification.objects.filter(
                phone_number=request.user.phone_number,
                is_used=False,
            ).latest('datetime_created')

            if verification.is_expired():
                messages.error(request, _('Validation code is expired. Please ask for a new code'))

            elif verification.code == entered_code:
                verification.is_used = True
                verification.save()

                request.user.phone_verified = True
                request.user.save()

                messages.success(request, _('Your phone number is verified'))
                return redirect('pages:home_page')

            else:
                messages.error(request, _('Your code is not valid'))

        except PhoneVerification.DoesNotExist:
            messages.error(request, _('Error happened during code validation'))

    return render(request, 'accounts/verify_phone.html')

@login_required
def resend_code(request):
    new_code = str(random.randint(100000, 999999))

    PhoneVerification.objects.filter(
        phone_number=request.user.phone_number,
        is_used=False,
    ).update(is_used = True)

    PhoneVerification.objects.create(
        phone_number=request.user.phone_number,
        code=new_code,
    )

    if send_sms_verification(request.user.phone_number, new_code):
        messages.success(request, _('New verification code was sent'))
    else:
        messages.error(request, _('Error sending sms message. Please try again'))

    return redirect('accounts:verify_phone')
