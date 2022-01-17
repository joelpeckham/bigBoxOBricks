# sync.py
# Written by Joel Peckham | joelskyler@gmail.com
# Last Updated : Jan 17, 2022
# This program was designed to run as a daemon on an Ubuntu VPS.
# The purpose of this program is to sync order information between
# Shippo, BrickLink, and Brick Owl. As orders are created on either
# Brick Owl or BrickLink, they must be added to Shippo. As order status
# changes on any site, the changes must be synced appropriately. 
# API keys for all three sites are stored in the api_keys.json file.

from lib2to3.pgen2 import token
import daemon           # We need this module so our script will always run as a daemon.
import requests         # We need this module to make HTTPs requests to the various APIs.
import shippo           # Shippo provies a wrapper module for the Shippo API, this should make this a little easier.
import json             # We need this module to read and write JSON files (such as api_keys.json).
import time             # We need this module to sleep for a few seconds between API calls.
import sys              # We need this module to exit the program when an error occurs.
import os               # We need this module to check if the api_keys.json file exists.
import logging          # We need this module to log errors to a file.
import datetime         # We need this module to get the current date and time, and do some date math.

from requests_oauthlib import OAuth1Session # We need this module to make OAuth1 requests to the BrickLink API.

# The first thing to do is to check if the api_keys.json file exists.
# If it doesn't, we need to exit the program.
if not os.path.isfile('api_keys.json'):
    print('api_keys.json file not found. Exiting program.')
    sys.exit()
# If the api_keys.json file exists, we need to read it.
with open('api_keys.json', 'r') as f:
    api_keys = json.load(f)


# Now that we have the API keys all sorted out, let's make sure they all work properly before we deamonize the script.
# We'll make session objects for each API, then send a test call to each one.
# If any of the calls fail, we'll exit the program.
try:
    # # The Shippo API has a testing option with a separate API key. Let's make a variable for it for debugging purposes.
    # currently_testing = True    
    # # We'll set the Shippo API key to the one we're currently using.
    # shippo.config.api_key = api_keys['shippo_test'] if currently_testing else api_keys['shippo_live']
    # # Then try to make a request with the Shippo API.
    # shippoShipments = shippo.Shipment.all()
    # # Just for testing, let's print the response to the console.
    # print(shippoShipments)

    # # Now let's test the brickowl API.
    # # We'll start by creating a session object for the BrickOwl API.
    # brickowl_session = requests.Session()
    # brickowl_order_url = 'https://api.brickowl.com/v1/order/list'
    # # We'll set the parameters for the request.
    # brickowl_params = {
    #     "key": api_keys['brick_owl']
    # }
    # # Then we'll make the request.
    # brickowl_response = brickowl_session.get(brickowl_order_url, params=brickowl_params)
    # # Just for testing, let's print the response to the console.
    # print(json.dumps(json.loads(brickowl_response.text), indent=2))

    # Now let's test the bricklink API. This one's a bit more complicated.
    # We'll start by creating a session object for the BrickLink API.
    bricklink_session = requests.Session()
    bricklink_order_url = 'https://api.bricklink.com/api/store/v1/orders'
    # Let's set the authorization header for the request. We're using Oauth 1 for this.
    oauth = OAuth1Session(client_key= api_keys['bricklink_consumer_key'], client_secret= api_keys['bricklink_consumer_secret'], resource_owner_key= api_keys['bricklink_token_value'], resource_owner_secret= api_keys['bricklink_token_secret'])

    # We'll set the parameters for the request.
    bricklink_params = {
        "status": "paid",
    }
    # Then we'll make the request.
    bricklink_response = oauth.get(bricklink_order_url, params=bricklink_params)

    # Just for testing, let's print the response to the console.
    print(json.dumps(json.loads(bricklink_response.text), indent=2))
    
    # Alright? If we've made it this far, we're good to go.

except Exception as e:
    print('Error in creating session objects. Exiting program.')
    print(e)
    sys.exit()

