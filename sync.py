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

# Now that we have all the API objects, let's make a list of all the orders that need to be synced over to Shippo.
# We'll start by making an empty list.
new_orders = [] 
# Then, we'll extend the list with all the new orders from Brick Owl.
new_orders.extend(brickOwlApi.getNewOrders())
# Then, we'll extend the list with all the new orders from Brick Link.
new_orders.extend(brickLinkApi.getNewOrders())
# Now let's push all the new orders to Shippo.
shippoApi.createOrders(new_orders)
# Now let's make sure that all the orders are in the correct state on every site.
# We'll start by making a dictionary of all the orders with their order IDs as keys.
order_dict = {}
# We'll now download all the orders from Shippo.
shippo_orders = shippoApi.getAllOrders()
# And Brick Owl...
brickOwl_orders = brickOwlApi.getAllOrders()
# And Brick Link...
brickLink_orders = brickLinkApi.getAllOrders()

# We'll also need some dictionaries to keep track of the orders that need to be updated.
# We'll start by making empty dictionaries.
shippo_update_dict = {}
brickOwl_update_dict = {}
brickLink_update_dict = {}

# Now let's loop through all the different order sources.
for storeName, orderList in [('Shippo', shippo_orders), ('Brick Owl', brickOwl_orders), ('Brick Link', brickLink_orders)]:
    # And loop through all the orders in each store.

    for order in orderList:
        # We'll add the order to the dictionary with its order ID as the key as long as it doesn't already exist.
        if order['id'] not in order_dict:
            order_dict[order['id']] = order
        else:
            # If the order already exists, we'll compare the updated_at values.
            # If the updated_at value on the order in the store is newer than the one in the dictionary, we'll update the dictionary.
            if datetime.strptime(order['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ') > datetime.strptime(order_dict[order['id']]['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ'):
                order_dict[order['id']] = order
                # And we'll add the order to the appropriate update dictionary.
                if storeName == 'Shippo':
                    shippo_update_dict[order['id']] = order
                elif storeName == 'Brick Owl':
                    brickOwl_update_dict[order['id']] = order
                elif storeName == 'Brick Link':
                    brickLink_update_dict[order['id']] = order

# Alright, now let's update the orders on each site.
# First, we'll update the Shippo orders.
shippoApi.updateOrders(shippo_update_dict)
# Then, we'll update the Brick Owl orders.
brickOwlApi.updateOrders(brickOwl_update_dict)
# And finally, we'll update the Brick Link orders.
brickLinkApi.updateOrders(brickLink_update_dict)

# That's it! ... for now.
