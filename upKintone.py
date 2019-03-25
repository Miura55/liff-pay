#!/usr/bin/python
# _*_ coding: utf-8 _*_

import requests
import os

def PostToKintone(userID, price, syohin, account):
	URL        = os.environ["KINTONE_APP_URL"]											# URL
	API_TOKEN  = os.environ["KINTONE_API_TOKEN"]
	appId = "3"
	record={'user_id':{'value' : userID}, 'price':{'value' : price},'syohin':{'value':syohin}, 'account':{"value":account}}
	data = {'app':appId,'record':record}
	headers = {"X-Cybozu-API-Token": API_TOKEN, "Content-Type" : "application/json"}
	resp=requests.post(URL+'/k/v1/record.json',json=data,headers=headers)
	return resp
