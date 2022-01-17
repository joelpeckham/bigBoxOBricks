# brickowl_api.py
# Written by Joel Peckham | joelskyler@gmail.com
# Last Updated : Jan 17, 2022
# This class is a wrapper for the Brick Owl API.
import requests

class BrickOwlAPI:
    def __init__(self, api_key) -> None:
        self.session = requests.Session()
        self.keyParam = {
            'key': api_key
        }
        
    def _get(self, url, params={}) -> requests.Response:
        params.update(self.keyParam)
        return self.session.get(url, params=params)
    
    def _post(self, url, params={}) -> requests.Response:
        params.update(self.keyParam)
        return self.session.post(url, params=params)
