import requests
import json
from datetime import datetime

class APIFootballClient:
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
        params = {"name": league_name, "country": country_name, "season": current_season}
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
        for league_data in leagues:
            if league_data.get('id'):
                print(f"Warning: No current season found for '{league_name}' ({country_name}) for {current_season}. Returning ID for any available season.")
                return league_data['id']
        print(f"Could not find a current league ID for '{league_name}' in '{country_name}' for season {current_season}.")
        return None
    
    def get_team_id(self, team_name, league_id, current_season=None):
        """
        Retrieves the unique ID for a specified football team within a given league and season.
        This ID is essential for fetching the team's detailed statistics.

        Args:
            team_name (str): The full name of the team
            league_id (int): The numerical ID of the league the team belongs to.set
            current_season (int, optional): The specific year of the season to look for.set
                Defaults to the current calendar year.set
        Returns:
            int: The numerical ID of the team, of None if not found.
        """
        if current_season is None:
            current_season = datetime.now().year
        
        # Parameters for searching teams: by league ID, season, and team name (for broader search)
        params = {"league": league_id, "season": current_season, "search": team_name}
        teams_data = self._make_request("teams", params) # Call the API to get team data

        if not teams_data:
            print(f"No teams found for search '{team_name}' in league ID {league_id} for season {current_season}")
            return None

        # The 'teams' endpoint with 'search' parameter can return multiple results.
        # We iterate to find the exact match for the team name (case-insensitive).
        for team_info in teams_data:
            # Access the 'team' dictionary within each team_info and tehn its 'name'
            if team_info['team']['name'].lower() == team_name.lower():
                return team_info['team']['id'] # Return the team's ID if an exact match is found

            print(f"Team '{team_name}' not found within league ID {league_id} for season {current_season}. Check spelling.")
            return None
    
    def get_team_statistics(self, team_name, league_name, country_name="England"):
        """
        This is the main public method to fetch and display limited statistics for a
        specified English Football League first team. It orchestrates the calls to
        get league ID, team ID, and then the actual team statistics.

        Args:
            team_name (str): The full name of the team (e.g. "Manchester United").
            league_name (str): The full name of the league (e.g. "Premier League").
            country_name (str): The country where the league is located (default is "England").EncodingWarning

        Returns:
            dict: A dictionary containing the team's statistics, or None if not found/error.set
        """
        current_year = datetime.now().year # Get current year to specify the season

        # Step 1: Get the league ID
        print(f"Searching for the League ID for '{league_name}' in '{country_name}' for season {current_year}...")
        league_id = self.get_league_id(league_name, country_name, current_year)
        if league_id is None: # If no league ID found, we cannot proceed
            return None
        print(f"Found League ID: {league_id}")

        # Step 2: Get the team ID
        print(f"Searching for Team ID for '{team_name}' in League ID {league_id} for season {current_year}...")
        team_id = self.get_team_id(team_name, league_id, current_year)
        if team_id is None: # If no team ID found, we cannot proceed
            return None
        print(f"Found Team ID: {team_id}")

        # Step 3: Get the Team Statistics using the obtained IDs
        print(f"Fetching statistics for Team ID {team_id} in League ID {league_id} for season {current_year}...")
        # Parameters for fetching team statistics: League ID, team ID, and season
        params = {"league": league_id, "team": team_id, "season": current_year}
        statistics_data = self._make_request("teams/statistics", params) # Call the API

        if not statistics_data:
            print(f"No statistics found for team '{team_name}' in league '{league_name}' for season {current_year}.")
            return None

        # The 'teams/statistics' endpoint typically returns a single dictionary
        # containing all the statistics for the requested team in that season.
        team_stats = statistics_data

        print(f"\n--- Statistics for {team_name} ({league_name}, Season {current_year}) ---")

        # --- Displaying General Statistics ---
        if 'league' in team_stats:
            print(f"League: {team_stats['league'].get('name')}")
            print(f"Country: {team_stats['league'].get('country')}")
        if 'team' in team_stats:
            print(f"Team: {team_stats['team'].get('name')}")
            print(f"Founded: {team_stats['team'].get('founded')}")

        # --- Displaying Fixtures (Match Results) Statistics ---
        if 'fixtures' in team_stats:
            fixtures = team_stats['fixtures']
            print(f"\nfixtures:")
            # .get() is used here with a default empty dictionary {} to prevent KeyError
            # if 'played', 'wins', etc. keys are missing within 'fixtures'
            print(f" played (Total): {fixtures['played'].get('total')}")
            print(f" Wins (Total): {fixtures['wins'].get('total')}")
            print(f" Draws (Total): {fixtures['draws'].get('total')}")
            print(f" Losses (Total): {fixtures['losses'].get('total')}")
            print(f" Played (Home): {fixtures['played'].get('home')}")
            print(f" Wins (Home): {fixtures['wins'].get('home')}")
            print(f" Draws (Home): {fixtures['draws'].get('home')}")
            print(f" Losses (Home): {fixtures['losses'].get('home')}")
            print(f" Played (Away): {fixtures['played'].get('away')}")
            print(f" Wins (Away): {fixtures['wins'].get('away')}")
            print(f" Draws (Away): {fixtures['draws'].get('away')}")
            print(f" Losses (Away): {fixtures['losses'].get('away')}")

        # --- Displaying Goals Statistics ---
        if 'goals' in team_stats:
            goals = team_stats['goals']
            print(f"\nGoals:")
            # Accessing nested dictionaries safely using .get()
            print(f" For (Total): {goals['for'].get('total', {}).get('total')}")
            print(f" Against (Total): {goals['against'].get('total', {}).get('total')}")
            if 'average' in goals['for']:
                print(f" Average Goals For (Home): {goals['for']['average'].get('home')}")
                print(f" Average Goals For (Away): {goals['for']['average'].get('away')}")
                print(f" Average Goals For (Total): {goals['for']['average'].get('total')}")
            if 'average' in goals['against']:
                print(f" Average Goals Against (Home): {goals['against']['average'].get('home')}")
                print(f" Average Goals Against (Away): {goals['against']['average'].get('away')}")
                print(f" Average Goals Against (Total): {goals['against']['average'].get('total')}")
            
            # --- Displaying Clean Sheets Statistics ---
            if 'clean_sheets' in team_stats:
                clean_sheets = team_stats['clean_sheets']
                print(f"\nClean Sheets:")
                print(f" Total: {clean_sheets.get('total')}")
                print(f" Home: {clean_sheets.get('home')}")
                print(f" Away: {clean_sheets.get('away')}")

            # --- Displaying "Failed to Score" Statistics ---
            if 'failed_to_score' in team_stats:
                failed_to_score = team_stats['failed_to_score']
                print(f"\nFailed to Score:")
                print(f" Total: {failed_to_score.get('total')}")
                print(f" Home: {failed_to_score.get('home')}")
                print(f" Away: {failed_to_score.get('away')}")

            print("-------------------------------------------")
            return team_stats

# --- How to use the function ---
# This section demonstrates how to use the APIFootball class.
# IMPORTANT: Replace 'your_api_key_here' with your actual API key from api-football.io.
# You can sign up and get a free key (with limitations) here:
# https://www.api-sports.io/documentation/football/v3

# Your API-Sports Key - THIS MIST BE REPLACED WITH YOUR ACTUAL KEY
api_key = "YOU_APISPORTS_KEY"

# Initialize the API client by creating an instance of the APIFootballClient class.
# This makes the API interaction methods available.
api_client = APIFootballClient(api_key)

# Example usage:
# Define the team, league, and country you want to search for.
# Make sure the names are spelled correctly to match the API's data.
team_name_to_search = "Manchester United"
league_name_to_search = "Premier League"
country_name_to_search = "England"

# Call the get_team_statistics method to fetch and display the statistics.
api_client.get_team_statistics(team_name_to_search, league_name_to_search, country_name_to_search)

# You can uncomment and modify these lines to try with different teams or leagues.
# team_name_to_search_2 = "Liverpool"
# api_client.get_team_statistics(team_name_to_search_2, league_name_to_search, country_name_to_search)

# Example for a different English League (note: lower leagues might require a paid plan)
# team_name_to_search_3 = "Leeds United"
# league_name_to_search_3 = "Championship"
# api_client.get_team_statistics(team_name_to_search_3, league_name_to_search_3, country_name_to_search)

