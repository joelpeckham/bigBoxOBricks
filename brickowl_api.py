# brickowl_api.py
# Written by Joel Peckham | joelskyler@gmail.com
# Last Updated : Jan 17, 2022
# This class is a wrapper for the Brick Owl API.
import requests, json
from order import Order, OrderStub
from pprint import pprint

class BrickOwlAPI:
    def __init__(self, api_key) -> None:
        self.session = requests.Session()
        self.keyParam = {
            'key': api_key
        }
        
    def _get(self, url, params={}) -> requests.Response:
        params.update(self.keyParam)
        return self.session.get(url, params=params)
    
    def _post(self, url, params={}, body = {}) -> requests.Response:
        params.update(self.keyParam)
        return self.session.post(url, params=params, data = json.dumps(body))

    def getAllOrders(self):
        url = "https://api.brickowl.com/v1/order/list"
        response = self._get(url, params={'limit': 1000000, 'list_type': 'store'})
        if response.status_code == 200:
            return [OrderStub('brickowl', o['order_id'], o['status']) for o in response.json()]
        else:
            return []
    
    def getOrderDetails(self, order_id):
        url = "https://api.brickowl.com/v1/order/view"
        response = self._get(url, params={'order_id': order_id})
        if response.status_code == 200:
            return Order('brickowl', response.json(), self.getOrderItems(order_id))
        else:
            return None
    
    def getOrderItems(self, order_id):
        url = "https://api.brickowl.com/v1/order/items"
        response = self._get(url, params={'order_id': order_id})
        if response.status_code == 200:
            res = response.json()
            return [{'title': i['name'], 'quantity': i['ordered_quantity'], 'sku':i['lot_id'],"weight": i["weight"],"weight_unit": "oz"} for i in res]
        else:
            return []
    
    def shipped(self, order_id):
        url = "https://api.brickowl.com/v1/order/set_status"
        response = self._post(url, params={'order_id': order_id, 'status_id': '5'})
        if response.status_code == 200:
            return True
        else:
            return False
        
if __name__ == '__main__':
    with open('api_keys.json') as f:
        keys = json.load(f)
    api = BrickOwlAPI(keys['brickowl'])
    orderList = api.getAllOrders()
    orderDeets = api.getOrderDetails(orderList[0].id)
    pprint(orderDeets)