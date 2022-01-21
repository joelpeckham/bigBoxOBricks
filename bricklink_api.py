# bricklink_api.py
# Written by Joel Peckham | joelskyler@gmail.com
# Last Updated : Jan 17, 2022
# This class is a wrapper for the BrickLink API.
import requests, json
from requests_oauthlib import OAuth1Session
from order import Order, OrderStub

class BrickLinkAPI:
    def __init__(self, consumer_key, consumer_secret, token, token_secret) -> None:
        self.session = OAuth1Session(client_key = consumer_key, client_secret=consumer_secret, resource_owner_key=token, resource_owner_secret=token_secret)
        
    def _get(self, url, params=None) -> requests.Response:
        return self.session.get(url, params=params)
    
    def _post(self, url, params=None) -> requests.Response:
        return self.session.post(url, params=params)

    def getAllOrders(self):
        res = self._get('https://api.bricklink.com/api/store/v1/orders')
        if res.status_code == 200:
            # print(json.dumps(res.json())[:100])
            return [OrderStub('bricklink', o['order_id'], o['status']) for o in res.json()['data']]
        else:
            print(res.status_code, res.text)
    
    def getOrderDetails(self, order_id):
        res = self._get(f'https://api.bricklink.com/api/store/v1/orders/{order_id}')
        if res.status_code == 200:
            return Order('bricklink', res.json()['data'])
        else:
            return None
    
    def getOrderItems(self, order_id):
        res = self._get(f'https://api.bricklink.com/api/store/v1/orders/{order_id}/items')
        if res.status_code == 200:
            return [{'title': i['item']['name'] + ' | ' + i['item']['no'], 'quantity': i['quantity'], 'sku':i['inventory_id']} for i in res.json()['data']]
        else:
            return []
    
    def shipped(self, order_id):
        res = self._post(f'https://api.bricklink.com/api/store/v1/orders/{order_id}/status', data={'field': 'status', 'value': 'SHIPPED'})
        if res.status_code == 200:
            return True
        else:
            return False

if __name__ == "__main__":
    with open('api_keys.json') as f:
        keys = json.load(f)
    api = BrickLinkAPI(keys['bricklink_consumer_key'], keys['bricklink_consumer_secret'], keys['bricklink_token'], keys['bricklink_token_secret'])
    orderList = api.getAllOrders()
    print(orderList)
    print(len(orderList))
    orderDeets = api.getOrderDetails(orderList[0].id)
    print(orderDeets)
