# bricklink_api.py
# Written by Joel Peckham | joelskyler@gmail.com
# Last Updated : Jan 17, 2022
# This class is a wrapper for the BrickLink API.
import requests
from requests_oauthlib import OAuth1Session

class BrickLinkAPI:
    def __init__(self, consumer_key, consumer_secret, token, token_secret) -> None:
        self.session = OAuth1Session(client_key = consumer_key, client_secret=consumer_secret, resource_owner_key=token, resource_owner_secret=token_secret)
        
    def _get(self, url, params=None) -> requests.Response:
        return self.session.get(url, params=params)
    
    def _post(self, url, params=None) -> requests.Response:
        return self.session.post(url, params=params)

    def getNewOrders(self):
        pass