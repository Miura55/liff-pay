#!/usr/bin/python
# _*_ coding: utf-8 _*_

import requests
import os

def PostToKintone(appId, userID, price, syohin, account):
	URL        = os.environ["KINTONE_APP_URL"]											# URL
	API_TOKEN  = os.environ["KINTONE_API_TOKEN"]
	record={'user_id':{'value' : userID}, 'price':{'value' : price},'syohin':{'value':syohin}, 'account':{"value":account}}
	data = {'app':appId,'record':record}
	headers = {"X-Cybozu-API-Token": API_TOKEN, "Content-Type" : "application/json"}
	resp=requests.post(url+'/k/v1/record.json',json=data,headers=headers)
	return resp
