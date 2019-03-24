#!/usr/bin/python
# _*_ coding: utf-8 _*_

import requests


URL        = "https://devksmpdi.cybozu.com:443"											# URL
APP_ID     = "3"																			# kintoneのアプリID
API_TOKEN  = "Kk5glri8sVOnkGVe2J0b5dgT5abzxpmOQWMKQvWX"										# kintoneのAPIトークン

userID  = "aaaaaaaaa"																		# 登録値(SmileID)
price = 1500
account																			# 登録値(SmileCount)


def PostToKintone(url, appId, apiToken, userID, price, account):
	record={'user_id':{'value' : userID}, 'price':{'value' : price},'syohin':{'value':syohin}, 'account':{"value":account}}
	data = {'app':appId,'record':record}
	headers = {"X-Cybozu-API-Token": apiToken, "Content-Type" : "application/json"}
	resp=requests.post(url+'/k/v1/record.json',json=data,headers=headers)
	return resp

if __name__ == '__main__':
	resp= PostToKintone(URL, APP_ID, API_TOKEN, userId, price, account)
	print(resp.text)
