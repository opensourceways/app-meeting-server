import json
import random

import requests
from django.test import TestCase

# Create your tests here.


def send_msg(phone, code):
    url = 'https://106.ihuyi.com/webservice/sms.php?method=Submit'
    data = {
        'password': 'ce87532ad62ecccecb6dae8b01dd321f ',
        'account': 'C35758895',
        'mobile': phone,
        'content': '您的验证码是：{}。请不要把验证码泄露给其他人。'.format(code),
        'format': 'json'
    }
    result = requests.post(url, data)
    # print(result.text)
    data = result.json()
    if data['code'] == 2:
        return True
    else:
        return False


if __name__ == '__main__':
    print(send_msg('18683791700', '1234'))
