# **Football Team Statistics Fetcher (API-Sports.io)**

This Python script provides a simple way to fetch and display limited statistics for an English Football League first team using the **API-Sports.io Football API**. It's designed to be easy to understand and use, especially for those new to API interactions.

## **Features**

* **Fetches Team Statistics:** Retrieves key data like matches played, wins, losses, draws, goals scored, goals conceded, clean sheets, and failed-to-score matches.  
* **League & Team ID Resolution:** Automatically finds the necessary league and team IDs based on names you provide.  
* **Error Handling:** Includes robust error handling for common issues such as network problems, invalid API keys, and API rate limits.  
* **Modular Design:** Uses a class to organize API interaction logic, making the code clean and reusable.

## **How it Works**

The script interacts with the api-sports.io Football API in a few steps:

1. **Initialization:** You provide your API key when creating an instance of the APIFootballClient.  
2. **League ID Lookup:** It first finds the unique numerical ID for the specified football league (e.g., "Premier League") and season.  
3. **Team ID Lookup:** Once the league ID is known, it then finds the unique numerical ID for your chosen team (e.g., "Manchester United") within that league and season.  
4. **Statistics Retrieval:** Finally, it uses both the league and team IDs to fetch detailed team statistics for the current season.  
5. **Output:** The collected statistics are then neatly printed to your console.

## **Prerequisites**

Before running the script, you'll need:

* **Python 3:** Ensure you have Python installed on your system.  
* **requests library:** This is used to make HTTP requests. You can install it using pip:  
  pip install requests

* **API-Sports.io API Key:**  
  * Go to [https://www.api-sports.io/documentation/football/v3](https://www.api-sports.io/documentation/football/v3).  
  * Sign up for an account and obtain your unique API key. The free plan provides limited daily requests, which should be sufficient for testing.

## **Usage**

1. **Save the Code:** Save the provided Python code as a .py file (e.g., get\_football\_stats.py).  
2. **Insert Your API Key:** Open the file and locate the line:  
   api\_key \= "YOUR\_APISPORTS\_KEY" \# Replace with your actual API key

   Replace "YOUR\_APISPORTS\_KEY" with the API key you obtained from api-sports.io.  
3. **Configure Team and League:** Adjust the team\_name\_to\_search, league\_name\_to\_search, and country\_name\_to\_search variables to specify the team and league you're interested in.  
   team\_name\_to\_search \= "Manchester United"  
   league\_name\_to\_search \= "Premier League"  
   country\_name\_to\_search \= "England"

4. **Run the Script:** Execute the Python file from your terminal:  
   python get\_football\_stats.py

The script will then print the requested football statistics to your console.