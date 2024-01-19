import configparser
import json

import requests
import random

from aiogram.utils.json import JSON

config = configparser.ConfigParser()
config.read("settings.ini")

TOKEN = config["Basic"]["TOKEN"]
API = config["Nowpayments"]["API"]
def checkPayment(paymentID):

    url = f"https://api.nowpayments.io/v1/payment/{paymentID}"

    payload = {}
    headers = {
        'x-api-key': f'{API}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    status = response.json()["payment_status"]
    price = response.json()["pay_amount"]
    payAddress = response.json()["pay_address"]
    crypto = response.json()["pay_currency"]
    price_amount = response.json()["price_amount"]
    return status,payAddress,price,crypto,price_amount

def createTopUp(price,crypto,chat_id):
    url = "https://api.nowpayments.io/v1/payment"
    payload = json.dumps({
  "price_amount": price,
  "price_currency": "gbp",
  "pay_currency": crypto,
  "ipn_callback_url": f"https://api.telegram.org/bot{TOKEN}"
                            f"/sendMessage?chat_id={chat_id}"
                            f"&text=Success+click+check",
  "order_id": "RGDBP-21314",
  "order_description": "leads",
  "is_fee_paid_by_user": True
})
    headers = {
  'x-api-key': f"{API}",
  'Content-Type': 'application/json'
}

    response = requests.request("POST", url, headers=headers, data=payload).json()
    try:
        address = response['pay_address']
        payment_id = response["payment_id"]
        pay_amount = response["pay_amount"]
        return address,payment_id,pay_amount
    except:
        return False, False, False

