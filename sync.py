# sync.py
# Written by Joel Peckham | joelskyler@gmail.com
# Last Updated : Jan 17, 2022
# This program was designed to run as a daemon on an Ubuntu VPS.
# The purpose of this program is to sync order information between
# Shippo, BrickLink, and Brick Owl. As orders are created on either
# Brick Owl or BrickLink, they must be added to Shippo. As order status
# changes on any site, the changes must be synced appropriately. 
# API keys for all three sites are stored in the api_keys.json file.

import requests                         # We need this module to make HTTPs requests to the various APIs.
import json                             # We need this module to read and write JSON files (such as api_keys.json).
import time                             # We need this module to sleep for a few seconds between API calls.
import sys                              # We need this module to exit the program when an error occurs.
import os                               # We need this module to check if the api_keys.json file exists.
import logging                          # We need this module to log errors to a file.
from datetime import datetime           # We need this module to get the current date and time, and do some date math.
from shippo_api import ShippoAPI        # We need this module to make Shippo API calls.
from brickowl_api import BrickOwlAPI    # We need this module to make Brick Owl API calls.
from bricklink_api import BrickLinkAPI  # We need this module to make Brick Link API calls.

# First we'll configure the logger.
logging.basicConfig(filename='sync.log', level=logging.INFO, format='%(asctime)s %(message)s')

# The first thing to do is to check if the api_keys.json file exists.
# If it doesn't, we need to exit the program.
if not os.path.isfile('api_keys.json'):
    print('api_keys.json file not found. Exiting program.')
    sys.exit()
# If the api_keys.json file exists, we need to read it.
with open('api_keys.json', 'r') as f:
    api_keys = json.load(f)


# Now that we have the API keys all sorted out, let's make objects for each API.
shippoApi = ShippoAPI(api_keys['shippo_test']) 
brickOwlApi = BrickOwlAPI(api_keys['brickowl'])
# Bricklink uses OAuth1, so we need to give it a few more parameters.
brickLinkApi = BrickLinkAPI(api_keys['bricklink_consumer_key'], api_keys['bricklink_consumer_secret'], api_keys['bricklink_token'], api_keys['bricklink_token_secret'])

# Now let's get all the orders from brickowl that have a status of 'paid'.
paidOrders = brickOwlApi.getPaidOrders()
# Let's extend the paidOrders list to include bricklink orders.
paidOrders.extend(brickLinkApi.getPaidOrders())

# Now we'll try to add each order to Shippo.
for order in paidOrders:
    try:
        # We need to make a Shippo API call to create an order.
        shippoApi.createOrder(order)
    except Exception as e:
        # If the error is anything other than a duplicate order, we need to log it.
        if 'Duplicate order' not in str(e):
            logging.error('Error creating Shippo order for order #' + str(order['order_id']) + ': ' + str(e))

# Now let's get all the orders from brickowl and bricklink that have a status of 'shipped'.
# We'll store these orders in a dictionary so we can easily access them by order_id.
shippedOrders = {o['order_id']: o for o in brickOwlApi.getShippedOrders()}
shippedOrders.update({o['order_id']: o for o in brickLinkApi.getShippedOrders()})

# Now we'll get all the Shippo orders that have a status of 'shipped'.
shippoShippedOrders = shippoApi.getShippedOrders()

# If there are any Shippo orders that are not in the shippedOrders list, we need to update the status of those orders in Brick Owl and Brick Link.
for order in shippoShippedOrders:
    if order['order_id'] not in shippedOrders:
        if order.source == 'brickowl':
            brickOwlApi.updateOrderStatus(order['order_id'], 'shipped')
        elif order.source == 'bricklink':
            brickLinkApi.updateOrderStatus(order['order_id'], 'shipped')
            