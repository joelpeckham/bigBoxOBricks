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
            return Order('brickowl', response.json())
        else:
            return None
        
if __name__ == '__main__':
    import argparse
    des = """BrickOwl API Wrapper. Requires an API key. This is a module and should not be run directly, but since you\'re reading this, you\'re probably interested in testing the module. Provide an API key as an argument to this script, and we\'ll run the tests."""
    parser = argparse.ArgumentParser(description=des)
    parser.add_argument('--key', help='API Key for BrickOwl. See https://www.brickowl.com/api_docs.', required=True)
    args = parser.parse_args()
    api = BrickOwlAPI(args.key)
    orderList = api.getAllOrders()
    orderDeets = api.getOrderDetails(orderList[0].id)
    pprint(orderDeets)