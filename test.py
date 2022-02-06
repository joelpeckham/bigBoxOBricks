from bricklink_api import BrickLinkAPI
from order import Order, OrderStub
import json
from pprint import pprint as pp
testorder = 18332181

with open('api_keys.json', 'r') as f:
        api_keys = json.load(f)

brickLinkApi = BrickLinkAPI(api_keys['bricklink_consumer_key'], api_keys['bricklink_consumer_secret'], api_keys['bricklink_token'], api_keys['bricklink_token_secret'])

order = brickLinkApi.getOrderDetails(testorder)
pp(order)
pp(order.items)