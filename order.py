# order.py
# Written by Joel Peckham | joelskyler@gmail.com
# Last Updated : Jan 17, 2022
# This is a class that represents an order.

class Order:
    def __init__(self, source, orderData):
        self.source = source
        builderFunctions = {
            'brickowl': self.buildBrickOwlOrder,
            'bricklink': self.buildBrickLinkOrder,
            'shippo': self.buildShippoOrder
        }
        self.data = builderFunctions[source](orderData)
        self.address = self.data['address']
        self.naitiveID = self.data['id']
        self.shippoID = self.data['shippo_id']
        self.status = self.data['status']
        self.statusCode = self.data['status_code']
        self.created = self.data['created_at']
        self.statusChanged = self.data['status_changed']
    
    def buildBrickOwlOrder(orderData):
        return {
            'id': orderData['order_id'],
            'shippo_id': "brickowl_" + str(orderData['order_id']),
            'address': {
                'first_name': orderData['ship_first_name'],
                'last_name': orderData['ship_last_name'],
                'country_code': orderData['ship_country_code'],
                'postal_code': orderData['ship_postal_code'],
                'street_1': orderData['ship_street_1'],
                'street_2': orderData['ship_street_2'],
                'city': orderData['ship_city'],
                'state': orderData['ship_state'],
            },
            'status': orderData['status'],
            'status_code': int(orderData['status_id']),
            'status_changed': None,
            'created_at': orderData['order_time']
        }
    def buildBrickLinkOrder(orderData):
        return {
            'id': orderData['order_id'],
            'shippo_id': "bricklink_" + str(orderData['order_id']),
            'address': {
                'first_name': orderData['shipping']['address']['name']['first'],
                'last_name': orderData['shipping']['address']['name']['last'],
                'country_code': orderData['shipping']['address']['country_code'],
                'postal_code': orderData['shipping']['address']['postal_code'],
                'street_1': orderData['shipping']['address']['address1'],
                'street_2': orderData['shipping']['address']['address2'],
                'city': orderData['shipping']['address']['city'],
                'state': orderData['shipping']['address']['state'],
            },
            'status': orderData['status'],
            'status_code': None,
            'status_changed': orderData['date_status_changed'],
            'created_at': orderData['date_ordered']
        }
    def buildShippoOrder(orderData):
        pass
