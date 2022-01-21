# shippo_api.py
# Written by Joel Peckham | joelskyler@gmail.com
# Last Updated : Jan 17, 2022
# This class is a wrapper for the Shippo API.

import requests, json
from order import Order, OrderStub

class ShippoAPI:
    def __init__(self, api_key) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"ShippoToken {api_key}"
        })
    
    def _get(self, url, params=None) -> requests.Response:
        return self.session.get(url, params=params)
    
    def _post(self, url, params=None, body=None) -> requests.Response:
        return self.session.post(url, params=params, json=body)
    
    def getAllOrders(self):
        url = "https://api.goshippo.com/v1/orders"
        orderList = []
        while url:
            res = self._get(url)
            if res.status_code == 200:
                orderList.extend([OrderStub('shippo', o['order_number'], o['order_status']) for o in res.json()['results']])
                url = res.json()['next']
            else:
                print(res.status_code, res.text)
                break
        return orderList

    def addOrder(self,order:Order):
        orderData = {
            "to_address":{
                "city": order.address['city'],
                "country": order.address['country_code'],
                "name": order.address['first_name'] + " " + order.address['last_name'],
                "state": order.address['state'],
                "street1": order.address['street_1'],
                "street2": order.address['street_2'],
                "zip": order.address['postal_code']
            },
            "order_number": order.source + '_' + str(order.naitiveID),
            "order_status": "PAID",
            "placed_at": order.created,
            "weight": order.weight,
            "weight_unit": "oz",
            "line_items": order.items

        }
        res = self._post("https://api.goshippo.com/v1/orders", body=orderData)
        if res.status_code == 201:
            return True
        else:
            print(res.status_code, res.text)
            return False
        

if __name__ == "__main__":
    with open('api_keys.json') as f:
        keys = json.load(f)
    api = ShippoAPI(keys['shippo_test'])
    orderList = api.getAllOrders()
    print(orderList)
    print(len(orderList))

