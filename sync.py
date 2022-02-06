# sync.py
# Written by Joel Peckham | joelskyler@gmail.com
# Last Updated : Jan 17, 2022
# This program was designed to run as a daemon on an Ubuntu VPS.
# The purpose of this program is to sync order information between
# Shippo, BrickLink, and Brick Owl. As orders are created on either
# Brick Owl or BrickLink, they must be added to Shippo. As order status
# changes on any site, the changes must be synced appropriately. 
# API keys for all three sites are stored in the api_keys.json file.

import json                             # We need this module to read and write JSON files (such as api_keys.json).
import sys                              # We need this module to exit the program when an error occurs.
import os                               # We need this module to check if the api_keys.json file exists.
import logging                          # We need this module to log errors to a file.
from datetime import datetime           # We need this module to get the current date and time, and do some date math.
from shippo_api import ShippoAPI        # We need this module to make Shippo API calls.
from brickowl_api import BrickOwlAPI    # We need this module to make Brick Owl API calls.
from bricklink_api import BrickLinkAPI  # We need this module to make Brick Link API calls.

# First we'll configure the logger.
currentDate = datetime.now().strftime('%Y-%m-%d')
logging.basicConfig(filename=f'/home/joel/integration/{currentDate}_sync.log', level=logging.INFO, format='%(asctime)s %(message)s',filemode='a')

try:
    logging.info("Starting sync.py")

    # The first thing to do is to check if the api_keys.json file exists.
    # If it doesn't, we need to exit the program.
    if not os.path.isfile('/home/joel/integration/api_keys.json'):
        logging.error('api_keys.json file not found. Exiting program.')
        sys.exit()
    # If the api_keys.json file exists, we need to read it.
    with open('api_keys.json', 'r') as f:
        api_keys = json.load(f)


    # Now that we have the API keys all sorted out, let's make objects for each API.
    shippoApi = ShippoAPI(api_keys['shippo_live']) 
    brickOwlApi = BrickOwlAPI(api_keys['brickowl'])
    # Bricklink uses OAuth1, so we need to give it a few more parameters.
    brickLinkApi = BrickLinkAPI(api_keys['bricklink_consumer_key'], api_keys['bricklink_consumer_secret'], api_keys['bricklink_token'], api_keys['bricklink_token_secret'])

    # Now we'll get all the order stubs from each source.
    shippoOrderStubs = shippoApi.getAllOrders()
    brickOwlOrders = brickOwlApi.getAllOrders()
    brickLinkOrders = brickLinkApi.getAllOrders()

    logging.info(f"Got {len(shippoOrderStubs)} shippo order stubs.")
    logging.info(f"Got {len(brickOwlOrders)} brickOwl order stubs.")
    logging.info(f"Got {len(brickLinkOrders)} brickLink order stubs.")

    # We'll filter through the brick owl orders and get the ones that have a status of 'Payment Received', 'Processing', or 'Processed'.
    # We'll also make sure that the order is not already in the shippo orders list.
    # Then, we'll add the order to the list of oders that need to be added to Shippo.
    ordersToAddToShippo = []

    for order in brickOwlOrders:
        if order.status in ['Processed']:
            if "brickowl_" + str(order.id) not in [o.id for o in shippoOrderStubs]:
                ordersToAddToShippo.append(order)
    # Now we'll do the same thing for the brick link orders. But for brick link, we'll only add orders that have a status of 'PAID' or 'PACKED'.
    for order in brickLinkOrders:
        if order.status in ['PACKED']:
            if "bricklink_" + str(order.id) not in [o.id for o in shippoOrderStubs]:
                ordersToAddToShippo.append(order)

    logging.info(f'{len(ordersToAddToShippo)} orders need to be added to Shippo.')
    logging.info(f'Adding: {ordersToAddToShippo}')

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

    logging.info(f'Got details for {len(ordersToAddToShippoWithDetails)} orders that need to be added to Shippo.')

    # Now we need to add the orders to Shippo.

    ordersAddedToShippo = []
    for order in ordersToAddToShippoWithDetails:
        if shippoApi.addOrder(order): 
            ordersAddedToShippo.append(order)

    logging.info(f'Added {len(ordersAddedToShippo)} orders to Shippo.')
    logging.info(f'Added: {ordersAddedToShippo}')

    # Now let's make sure that the orders are in the correct status.
    # We'll start by getting all the orders from Shippo that have the status of "SHIPPED".
    shippedShippoOrderIds = [o.id for o in shippoOrderStubs if o.id and o.status == "SHIPPED"]

    logging.info(f'{len(shippedShippoOrderIds)} orders are in the Shippo "SHIPPED" status.')

    for order_id in shippedShippoOrderIds:
        if len(order_id.split('_')) == 2:
            source, order_id = order_id.split('_')
            if source == 'brickowl':
                if order_id in [o.id for o in brickOwlOrders if o.status in ['Payment Received', 'Processing', 'Processed']]:
                    if brickOwlApi.shipped(order_id):
                        logging.info(f'Marked brickOwl order {order_id} as shipped.')
                    else:
                        logging.error(f'Failed to mark brickOwl order {order_id} as shipped.')
            elif source == 'bricklink':
                if order_id in [o.id for o in brickLinkOrders if o.status in ['PAID', 'PACKED']]:
                    if brickLinkApi.shipped(order_id):
                        logging.info(f'Marked brickLink order {order_id} as shipped.')
                    else:
                        logging.error(f'Failed to mark brickLink order {order_id} as shipped.')

    logging.info("Finished sync.py")
    # Assuming this works, we're done for now!
except Exception as e:
    logging.error(e)
    print(e)