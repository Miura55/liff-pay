import os
from flask import Flask, request, abort, render_template, redirect
import requests
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from linebot import (
    LineBotApi
)
from linebot.models import (
    TextSendMessage,
    FlexSendMessage,
    BubbleContainer,
    StickerSendMessage
)
line_bot_api = LineBotApi('kF60SPieYOqUrOxN6bmTCep2/sb+KtZjeEOLEBt27bwvunWazgXJlGIvnLAw7TNqnt4UAZC1She6HME4WO6Eh+yjuMWyyZNkYTKq0RzJQED0tccBgnB8GXn04yUP5dl5jN4ZSur67zm6EdlwG/1DaVGUYhWQfeY8sLGRXgo3xvw=')
app = Flask(__name__, static_folder='static')
bootstrap = Bootstrap(app)
CORS(app)

import json
import shelve
import uuid

class LinePay(object):

    DEFAULT_ENDPOINT = 'https://sandbox-api-pay.line.me/'
    VERSION = 'v2'


    def __init__(self, channel_id, channel_secret, redirect_url):
        self.channel_id = channel_id
        self.channel_secret = channel_secret
        self.redirect_url = redirect_url

    def reserve(self, product_name, amount, currency, order_id, UserId, **kwargs):
        url = '{}{}{}'.format(self.DEFAULT_ENDPOINT, self.VERSION, '/payments/request')
        data = {**
                {
                    'productName':product_name,
                    'amount':amount,
                    'currency':currency,
                    'confirmUrl':'https://{}{}'.format(request.environ['HTTP_HOST'], self.redirect_url),
                    'orderId':order_id,
                },
                **kwargs}
        headers = {'Content-Type': 'application/json',
                   'X-LINE-ChannelId':self.channel_id,
                   'X-LINE-ChannelSecret':self.channel_secret}
        response = requests.post(url, headers=headers, data=json.dumps(data).encode("utf-8"))

        if int(json.loads(response.text)['returnCode']) == 0:
            with shelve.open('store') as store:
                # just for prototyping
                store[str(json.loads(response.text)['info']['transactionId'])] = {'productName': product_name, 'amount': amount, 'currency': currency, 'user':UserId}
            return json.loads(response.text)

        else:
            abort(400, json.loads(response.text)['returnCode'] + ' : ' + json.loads(response.text)['returnMessage'])

    def confirm(self, transaction_id):
        transaction_info = {}
        with shelve.open('store') as store:
            transaction_info = store[transaction_id]
            print(transaction_info)

        if len(transaction_info) == 0:
            abort(400, 'reservation of this transaction id is not exists')

        url = '{}{}{}'.format(self.DEFAULT_ENDPOINT, self.VERSION, '/payments/{}/confirm'.format(transaction_id))
        data = {
                'amount':transaction_info['amount'],
                'currency':transaction_info['currency'],
                }
        headers = {'Content-Type': 'application/json',
                   'X-LINE-ChannelId':self.channel_id,
                   'X-LINE-ChannelSecret':self.channel_secret}
        response = requests.post(url, headers=headers, data=json.dumps(data).encode("utf-8"))
        print(url)
        print(data)
        print(headers)
        return transaction_info

# get it in https://pay.line.me/jp/developers/techsupport/sandbox/creation?locale=ja_JP
chennel_id = '1557966586'
channel_secret = '8041bcad5f15256c30408f1fbb051777'
callback_url = '/callback'

"""
# get these at https://pay.line.me/center/notice/list after creating sandbox sandbox
chennel_id = YOUR_LINE_PAY_CHANNEL_ID
channel_secret = YOUR_LINE_PAY_CHANNEL_SECRET
callback_url = '/callback'
"""
pay = LinePay(chennel_id, channel_secret, callback_url)

@app.route("/")
def render_index():
    item_id = request.args.get("itemName")
    return render_template('index.html', data=item_id)

@app.route("/reserve/<UserId>/<itemName>", methods=["POST"])
def redirect_to_pay(UserId=None, itemName=None):
    print("got: ", request.form)
    data = {"product_name": itemName,
            'amount':'1500',
            'currency':'JPY',
            'order_id':uuid.uuid4().hex,
            "UserId":UserId,
            # optional values can be set. see https://pay.line.me/file/guidebook/technicallinking/LINE_Pay_Integration_Guide_for_Merchant-v1.1.2-JP.pdf
            'productImageUrl':'https://{}{}'.format(request.environ['HTTP_HOST'], '/static/item_image.jpg')
            }
    transaction_info = pay.reserve(**data)
    print(transaction_info['info']['paymentUrl']['web'])
    # return redirect(transaction_info['info']['paymentUrl']['web'])
    return transaction_info['info']['paymentUrl']['web']

@app.route("/callback")
def callback_from_pay():
    transaction_info = pay.confirm(request.args.get('transactionId'))
    print("trasaction: ",transaction_info)
    # push message to trasaction_info['user']
    userId = transaction_info['user']
    profile = line_bot_api.get_profile(userId)

    import upKintone
    URL        = "https://devksmpdi.cybozu.com:443"											# URL
    APP_ID     = "3"																			# kintoneのアプリID
    API_TOKEN  = "Kk5glri8sVOnkGVe2J0b5dgT5abzxpmOQWMKQvWX"
    price = "1500"
    resp = upKintone.PostToKintone(URL, APP_ID, API_TOKEN, userId, price, profile)
    print(resp.text)

    with open("recipt.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
        line_bot_api.push_message(
            userId,
                [
                    FlexSendMessage(
                        alt_text="レシート",
                        contents=BubbleContainer.new_from_json_dict(json_data)
                    ),
                    StickerSendMessage(
                        package_id=2,
                        sticker_id=41
                    )
                ]
            )
    return render_template('purchased.html', **transaction_info)

app.errorhandler(400)
def handler_error_400(error):
    return error

if __name__ == '__main__':
    app.debug = True;
    app.run()
