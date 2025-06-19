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
        try:
            # Construct the full URL for the request
            url = f"{self.base_url}/{endpoint}"
            # Send the GET request to the API with the specified headers and parameters
            response = requests.get(url, headers=self.headers, params=params)
            # Raise an HTTPError for bad responses (4xx or 5xx)
            # This helps us catch errors like "Not Found" or "Unauthorized" easily.
            response.raise_for_status()
            # Parse the JSON response from the API into a Python dictionary
            data = response.json()

            # API-Football typically returns a 'response' field that contains the actual data we want.
            # If the 'response' field is not present, we return an empty list.
            if data and data.get('response'):
                return data['response']
            else:
                # If the 'resposnse' key is empty or missing, check for specific API-side errors.
                if data.get('errors'):
                    print(f"API Error for {endpoint}: with params {params}: {data['errors']}")
                return [] # Return an empty list if no valid response or specific errors are found.
        # --- Error Handling for network and HTTP issues ---
        # Catch specific HTTP errors
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} for endpoint {endpoint} with params {params}")
            if response.status_code == 403:
                print("Error 403: Forbidden. Your API key may be invalid or you may not have access to this endpoint.")
            elif response.status_code == 429:
                print("Error 429: Too Many Requests. You have exceeded your API rate limit.")
            return None # Return None to indicate an error occurred.
        # Catch connection-related errors (e.g., no internet)
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred: {conn_err} - Check your Internet connection.")
            return None # Return None to indicate an error occurred.
        # Catch timeout errors if the server takes too long to respond
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error occurred: {timeout_err} - The requeest took too long to respond.")
            return None
        # Catch any other general request exceptions
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err} for endpoint {endpoint} with params {params}")
            return None
        # Catch errors if the response body isn't valid JSON
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON response from {endpoint}. The API might have returned non-JSON data.")
            return None
        
    def get_league_id(self, league_name, country_name="England", current_season=None):
        """
        Retrieves the unique ID for a specified football league within a given coutry and season.
        This ID is necessary for subsequent API calls to get team statistics.
        
        Args:
            league_name (str): The full name of the league (e.g., "Premier League").
            country_name (str): The country where the league is located (default is "England").
            current_season (int, optional): The specific year of the season to look for.
                If not provided, the current year is used.
                
        Returns: 
            int: The numerical ID of the league, or None if not found.
        """
        if current_season is None:
            current_season = datetime.now().year # Get the current year if not specified.
        # Parameters for searching leagues: by name and country
        params = {
            "name": league_name,
            "country": country_name,
            "season": current_season
        leagues = self._make_request("leagues", params) # Call the API to get league data

        if not leagues:
            print(f"No leagues found for {league_name} in {country_name} for the season {current_season}.")
            return None # Return None if no leagues are found
        
        # Loop through the leagues to find the one that matches the name and country
        for league_data in leagues:
            # Each league entry can contain maultiple seasons, We need to find the current one
            for season_info in league_data.get('seasons', []):
                # Check if the season year matches and if it's marked as the 'current' season
                if season_info.get('year') == current_season and season_info.get('current', False):
                    # Return the league ID if found
                    return league_data['id']
        # If no 'current' season for the specified year is explicitly found,
        # we try to return the ID of *any* season found for that league.
        # This is a fallback in case the 'current' flag isn't perfectly up-to-date in the API.
        for league_data in leaggues:
            if league_data.get('id'):
                print(f"Warning: No current season found for '{league_name}' ({country_name}) for {current_season}. Returning ID for any available season.")
                return league_data['id']
        print(f"Could not find a current league ID for '{league_name}' in '{country_name}' for season {current_season}.")
        return None