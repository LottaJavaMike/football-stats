import requests
import json
from datetime import datetime

class APIFootball:
    """
    This class is designed to interact with the API-Football service.
    It encapsulates all the logic for making requests to the API and processing the responses, 
    making it easier to manage and reuse in different parts of an application.
    """
    def __init__(self, api_key):
        """
        Initializes the APIFootball instance with the provided API key.
        
        :param api_key: Your API key for accessing the API-Football service.
        """
        self.api_key = api_key
        # The base URL for the API-Football service. All requests will be made to this URL.
        # "x-apisports-key" is the header used for authentication.
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-apisports-key": self.api_key,
        }
    def _make_request(self, endpoint, params=None):
        """
        A private helper method (indicated by the leading underscore) to handle
        the actual HTTP GET requests to the API. This centralizes error handling and repoonse parsing, so 
        we don't repeat ourselves in every method.
        
        Args:
            endpoint (str): The specific part of the API URL you want to hit (e.g, "leagues". "teams").
            params (dict, optional): A dictionary of query parameters to send with the request. These filter the data you receive (
            e.g. {"country": "England"}). Defaults to None.
        Returns:
            list or dict: The 'response' field from the API's JSON output, or an empty list/none if there's an error or no data.
        """