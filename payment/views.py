from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import HttpResponseForbidden

import requests
import json

from orders.models import Order

@login_required
def payment_process_sandbox(request):
    order_id = request.session['order_id']
    order = get_object_or_404(Order, pk=order_id)
    if order.user == request.user:
        if order.is_paid:
            messages.success(request, _('You have already paid for this order. You can enjoy using the products'))
            return order.get_absolute_url()

        # Gathering data to send request to zarinpal
        rial_total_price = order.get_total_price() * 10
        zarinpal_sandbox_request_url = 'https://sandbox.zarinpal.com/pg/v4/payment/request.json'
        request_data = {
            'merchant_id': settings.ZARINPAL_MERCHANT_ID,
            'amount': rial_total_price,
            'description': f'#{order_id}- {order.user.first_name} {order.user.last_name}',
            'callback_url': request.build_absolute_uri(reverse('payment:payment_callback_sandbox')),
        }
        request_header = {
            "accept": "application/json",
            "content-type": "application/json",
        }

        # Send request to zarinpal and analyze the response
        response = requests.post(url=zarinpal_sandbox_request_url, data=json.dumps(request_data), headers=request_header)

        data = response.json()['data']
        errors = response.json()['errors']

        code = data.get('code')
        message = data.get('message')
        authority = data.get('authority')

        if all([len(errors) == 0, code == 100, authority, message == 'Success']):
            order.zarinpal_authority = authority
            order.save()

            zarinpal_sandbox_redirect_url = 'https://sandbox.zarinpal.com/pg/StartPay/{authority}'.format(authority=authority)
            return redirect(zarinpal_sandbox_redirect_url)

        messages.error(request, _('Some errors happened from Zarinpal'))
        messages.error(request, errors['message'])
        message.info(request, _('Please try again or contact support. We can only hold your order for 15 minutes'))
        return redirect('orders:order_confirm', pk=order_id)
    return HttpResponseForbidden('<h1>Error 403 Forbidden')


@login_required
def payment_callback_sandbox(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, pk=order_id)

    payment_status = request.GET.get('Status')
    payment_authority = request.GET.get('Authority')

    if not payment_authority == order.zarinpal_authority:
        messages.error(request, _('Your Zarinpal-authority-code does not match the authority of the request'))
        return redirect('orders:order_detail', pk=order_id)

    if payment_status == 'OK':
        # Gather data to send to zarinpal for confirmation
        rial_total_price = order.get_total_price() * 10
        zarinpal_verify_url = 'https://sandbox.zarinpal.com/pg/v4/payment/verify.json'
        request_data = {
            'merchant_id': settings.ZARINPAL_MERCHANT_ID,
            'amount': rial_total_price,
            'authority': payment_authority,
        }
        request_header = {
            "accept": "application/json",
            "content-type": "application/json",
        }

        response = requests.post(url=zarinpal_verify_url, data=json.dumps(request_data), headers=request_header)

        data = response.json()['data']
        errors = response.json()['data']

        validation_code = data.get('code')
        ref_id = data.get('ref_id')

        if len(errors) > 0:
            messages.error(request, _('Payment Failed. Some errors happened from Zarinpal'))
            messages.error(request, errors['message'])
            order.cancel_order_if_payment_failed(request=request)

        elif validation_code == 101:
            messages.info(request, _('Payment already completed before. Check out your order status'))

        if len(errors) == 0 and validation_code == 100:
            order.zarinpal_ref_id = ref_id
            order.zarinpal_data = str(data)
            order.activate_order()
            messages.success(request, _('Payment successfully completed'))
            messages.success(request, _('Your order is getting processed'))
            return render(request, 'payment/payment_success.html', {'order': order})

    else: # if status == 'NOK':
        messages.error(request, _('Payment failed. Please contact support.'))

    return redirect('orders:order_detail', pk=order_id)


@login_required
def payment_process(request):
    pass


@login_required
def payment_callback(request):
    pass
