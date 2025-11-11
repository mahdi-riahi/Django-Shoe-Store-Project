from django.utils.translation import gettext as _
from django.conf import settings
import requests


def send_sms_verification(phone_number, code):
    message = _(f'JC Classic Leather \nYour validation code is {code}. Do not share it with others')

    # Kavehnegar
    # try:
    #     data = {
    #         'receptor': phone_number.replace('+', ''),
    #         'message': message,
    #     }
    #
    #     kavehnegar_api_key = settings.KAVEHNEG_API_KEY
    #     kavehnegar_url = f"https://api.kavenegar.com/v1/{kavehnegar_api_key}/sms/send.json"
    #     response = requests.post(url=kavehnegar_url, data=data)
    #     if response.status_code == 200:
    #         return True
    #     print(response.text)
    #     return False
    #
    # except Exception as e:
    #     print(f'sms error: {e}')
    #     return False

    print(phone_number, ":", message)
    return True
