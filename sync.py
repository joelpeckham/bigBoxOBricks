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
from order import Order                 # We need this module to store and manipulate order information.
from order import OrderStub             # We need this module to store and manipulate order information.

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

# Now we'll get all the order stubs from each source.
shippoOrderStubs = shippoApi.getAllOrders()
brickOwlOrders = brickOwlApi.getAllOrders()
brickLinkOrders = brickLinkApi.getAllOrders()

# We'll filter through the brick owl orders and get the ones that have a status of 'Payment Received', 'Processing', or 'Processed'.
# We'll also make sure that the order is not already in the shippo orders list.
# Then, we'll add the order to the list of oders that need to be added to Shippo.
ordersToAddToShippo = []
for order in brickOwlOrders:
    if order.status in ['Payment Received', 'Processing', 'Processed']:
        if "brickowl_" + str(order.id) not in [o.id for o in shippoOrderStubs]:
            ordersToAddToShippo.append(order)
# Now we'll do the same thing for the brick link orders. But for brick link, we'll only add orders that have a status of 'PAID' or 'PACKED'.
for order in brickLinkOrders:
    if order.status in ['PAID', 'PACKED']:
        if "bricklink_" + str(order.id) not in [o.id for o in shippoOrderStubs]:
            ordersToAddToShippo.append(order)

print(f'{len(ordersToAddToShippo)} orders need to be added to Shippo.')

# Now we need to get order details for each order that needs to be added to Shippo.
# The details will include the address and other important information.
ordersToAddToShippoWithDetails = []
for order in ordersToAddToShippo:
    if order.source == 'brickowl':
        orderDetails = brickOwlApi.getOrderDetails(order.id)
        ordersToAddToShippoWithDetails.append(orderDetails)
    elif order.source == 'bricklink':
        orderDetails = brickLinkApi.getOrderDetails(order.id)
        ordersToAddToShippoWithDetails.append(orderDetails)

print(f'Got details for {len(ordersToAddToShippoWithDetails)} orders that need to be added to Shippo.')

# Now we need to add the orders to Shippo.

ordersAddedToShippo = []
for order in ordersToAddToShippoWithDetails:
    if shippoApi.addOrder(order): 
        ordersAddedToShippo.append(order)

print(f'Added {len(ordersAddedToShippo)} orders to Shippo.')