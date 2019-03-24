#!/usr/bin/python
# _*_ coding: utf-8 _*_

import requests



def PostToKintone(url, appId, apiToken, userID, price, account):
	record={'user_id':{'value' : userID}, 'price':{'value' : price},'syohin':{'value':syohin}, 'account':{"value":account}}
	data = {'app':appId,'record':record}
	headers = {"X-Cybozu-API-Token": apiToken, "Content-Type" : "application/json"}
	resp=requests.post(url+'/k/v1/record.json',json=data,headers=headers)
	return resp
