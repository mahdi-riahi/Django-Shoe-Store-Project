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
    # print(f'Order found:{order.id}')
    if order.user == request.user:
#         print("order's user == request's user")
        if order.is_paid:
#             print('Order is paid')
            messages.success(request, _('You have already paid for this order. You can enjoy using the products'))
            return order.get_absolute_url()

        # Gathering data to send request to zarinpal
        rial_total_price = order.get_total_price() * 10
        zarinpal_sandbox_request_url = 'https://sandbox.zarinpal.com/pg/v4/payment/request.json'
        request_data = {
            'merchant_id': settings.ZARINPAL_MERCHANT_ID,
            'amount': rial_total_price,
            'description': f'#{order_id} - {order.user.first_name} {order.user.last_name}',
            'callback_url': request.build_absolute_uri(reverse('payment:payment_callback_sandbox')),
        }
        request_header = {
            "accept": "application/json",
            "content-type": "application/json",
        }
#         print('Sending request to zarinpal')

        # Send request to zarinpal and analyze the response
        response = requests.post(url=zarinpal_sandbox_request_url, data=json.dumps(request_data), headers=request_header)

        data = response.json()['data']
        errors = response.json()['errors']
#         print(f'response={response.json()}\ndata={data}\nerrors={errors}')

        code = data.get('code')
        message = data.get('message')
        authority = data.get('authority')

        if all([len(errors) == 0, code == 100, authority, message == 'Success']):
#             print('All good. Ready to redirect')
            order.zarinpal_authority = authority
            order.save()

            zarinpal_sandbox_redirect_url = 'https://sandbox.zarinpal.com/pg/StartPay/{authority}'.format(authority=authority)
            return redirect(zarinpal_sandbox_redirect_url)

#         print('Not all conditions were True')
        messages.error(request, _('Some errors happened from Zarinpal'))
        messages.error(request, errors['message'])
        messages.info(request, _('Please try again or contact support. We can only hold your order for 15 minutes'))
        return redirect('orders:order_confirm', pk=order_id)
#     print(f'Order_user != request_user. forbidden')
    return HttpResponseForbidden('<h1>Error 403 Forbidden')


@login_required
def payment_callback_sandbox(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, pk=order_id)
#     print(f'order found {order.id}')

    payment_status = request.GET.get('Status')
    payment_authority = request.GET.get('Authority')
#     print(f'payment_status:{payment_status}, payment_authority:{payment_authority}, order.zarinpal_authority:{order.zarinpal_authority}')

    if payment_authority != order.zarinpal_authority:
        messages.error(request, _('Your Zarinpal-authority-code does not match the authority of the request'))
#         print('Failed: authorities dont match')
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
#         print('Status is ok. Ready to post request to zarinpal')

        response = requests.post(url=zarinpal_verify_url, data=json.dumps(request_data), headers=request_header)

        data = response.json()['data']
        errors = response.json()['errors']
#         print(f'response={response.json()}')
#         print(f'data={data}\nerrors={errors}')

        validation_code = data.get('code')
        ref_id = data.get('ref_id')

        if len(errors) > 0:
            messages.error(request, _('Payment Failed. Some errors happened from Zarinpal'))
            messages.error(request, errors['message'])
            order.cancel_order_if_payment_failed(request=request)
#             print('len(errors)>0  --> failed. order canceled')

        elif validation_code == 101:
            messages.info(request, _('Payment already completed before. Check out your order status'))
#             print('validation_code101: already paid')

        if len(errors) == 0 and validation_code == 100:
            order.zarinpal_ref_id = ref_id
            order.zarinpal_data = str(data)
            order.activate_order()
#             print('Payment successful')
            messages.success(request, _('Payment successfully completed'))
            messages.success(request, _('Order is activated for you. you can trace it here'))
            messages.success(request, _('Your order is getting processed'))
            return redirect('orders:order_detail', pk=order_id)

    else: # if status == 'NOK':
        messages.error(request, _('Payment failed. Please contact support.'))
        order.cancel_order_if_payment_failed(request=request)
#         print('status != OK')

    return redirect('orders:order_detail', pk=order_id)


@login_required
def payment_process(request):
    pass


@login_required
def payment_callback(request):
    pass
