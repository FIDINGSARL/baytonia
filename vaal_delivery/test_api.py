import requests
import json
BASE = "https://api.vaal.me/api"



def get_token():
	headers = {'Content-Type':'Application/json'}
	data = {
		"username": "BAYTONIA",
		"password": "123Bayt"
	}
	url = "{BASE}/auth".format(BASE=BASE)
	res = requests.post(url, data).json()
	print(res)
	{'success': True, 'message': 'Token Generated', 
	'details': {'userid': 3703517413, 'x-auth': 
	'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOjM3MDM1MTc0MTMsImFjY2VzcyI6ImF1dGgiLCJpYXQiOjE1MzY4Nzc5MzMsImV4cCI6MTUzNjk2NDMzM30.lPpxEUlHs3va6Y0NeEg-Pe3zInYiG9PsD6Uwzikr6DQ'}}
	# '{"success":true,"message":"Token G/enerated","details":{"userid":3703517413,"x-auth":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOjM3MDM1MTc0MTMsImFjY2VzcyI6ImF1dGgiLCJpYXQiOjE1MzY4Nzc4OTMsImV4cCI6MTUzNjk2NDI5M30.D_l9sTwOpQoR0KxZjNjW-zQtNJzTtS930jwPBEplYhs"}}'


def get_orders():
	Auth = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOjM3MDM1MTc0MTMsImFjY2VzcyI6ImF1dGgiLCJpYXQiOjE1MzY4Nzc5MzMsImV4cCI6MTUzNjk2NDMzM30.lPpxEUlHs3va6Y0NeEg-Pe3zInYiG9PsD6Uwzikr6DQ"
	headers = {'Content-Type':'Application/json', 'x-auth': Auth}
	data = {
		"username": "BAYTONIA",
		"password": "123Bayt"
	}
	url = "{BASE}/orders".format(BASE=BASE)
	res = requests.get(url, headers=headers).json()
	# {'id': 44593, 'order_id': 49592118, 'user_id': 3703517413, 
	# 'pickup_address': 'جدة - من داخل جدة', 'drop_address': 'Jeddah', 
	# 'price': '346.00', 'service_tax': '0.00', 'receiver_name': 'رابعه ناجي', 
	# 'mobile': '966505358845', 'date': 'August 25, 2018, 7:38 pm', 'order_status': 2, 

	# 'original_price': '346.00', 'distance': 0, 'report_date': '2018-08-24T21:00:00.000Z', 
	# 'payment_mode': 'COD', 'delivery_date': 'August 27, 2018, 11:41 am', 'barcode': '49592118',
	#  'product_details': 'kitchenware ( handle with care ) 43243 ', 'received_driver': '', 
	#  'deliver_driver': '75', 'product_weight': '1.000', 'extra_weight_cost': '0.00', 
	#  'district': 'خلاصه الزهر حي النهضه شارع حراء حي النهضه فيلا 11'}
	print(res)

def get_orders_status(order_id):
	Auth = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOjM3MDM1MTc0MTMsImFjY2VzcyI6ImF1dGgiLCJpYXQiOjE1MzY4Nzc5MzMsImV4cCI6MTUzNjk2NDMzM30.lPpxEUlHs3va6Y0NeEg-Pe3zInYiG9PsD6Uwzikr6DQ"
	headers = {'Content-Type':'Application/json', 'x-auth': Auth}
	data = {
		"username": "BAYTONIA",
		"password": "123Bayt"
	}
	url = "{BASE}/orders/{order_id}".format(BASE=BASE, order_id=order_id)
	url = "{BASE}/order/status/{order_id}".format(BASE=BASE, order_id=order_id)
	res = requests.get(url, headers=headers).json()
	print(res)

def add_orders():
	{
		"orders" : [
				{
					"drop_address": "drop address 1",
					"receiver_name": "Client 1",
					"mobile_number": 123,
					"cod": 0,
					"details": "Street 1",
					"weight": 10,
					"additional_info": "district 1"
				},
				{
					"drop_address": "drop address 2","receiver_name": "Client 2",
					"mobile_number": 456,
					"cod": 200,
					"details": "Street 2",
					"weight": 20,
					"additional_info": "district 2"
				},
				{
					"drop_address": "drop address 3",
					"receiver_name": "Client 3",
					"mobile_number": 678,
					"cod": 300,
					"details": "Street 3",
					"weight": 30,
					"additional_info": "district 3"
				}
		]
	}
get_orders_status(16218350)