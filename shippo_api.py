# shippo_api.py
# Written by Joel Peckham | joelskyler@gmail.com
# Last Updated : Jan 17, 2022
# This class is a wrapper for the Shippo API.

import shippo

class ShippoAPI:
    def __init__(self, api_key) -> None:
        shippo.options.api_key = api_key
        