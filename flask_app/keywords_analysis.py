import requests
from config import Config
import os
from datetime import datetime
import pycountry
from backlinks import get_db_connection  

db = get_db_connection()  # Replace with your specific database name
keywords_collection = db.keywords  

def fetch_keyword_suggestions(keyword, search_engine="google", country="us"):
    """
    Fetch keyword suggestions from the API and store them in the 'keywords' collection in MongoDB.

    Args:
        keyword (str): The main keyword to analyze.
        search_engine (str): The search engine to use (default: "google").
        country (str): The country code for the search (default: "us").

    Returns:
        dict: A dictionary containing keyword suggestions and related questions.
    """
    url = "https://ahrefs2.p.rapidapi.com/keyword_suggestions"
    country = get_country_code(country)
    querystring = {"keyword": keyword, "se": search_engine, "country": country}

    headers = {
        "x-rapidapi-key": os.getenv('API_KEY2'),  # Fetch API key from environment variable
        "x-rapidapi-host": "ahrefs2.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx
        data = response.json()

        if data.get("status") == "success":
            suggestions = {
                "keyword": keyword,
                "country": country,
                "Ideas": data.get("Ideas", []),
                "Questions": data.get("Questions", []),
                "date": datetime.utcnow()  # Add current UTC timestamp
            }

            # Insert the suggestions data into the 'keywords' collection
            keywords_collection.insert_one(suggestions)

            return suggestions  # Return the data for the caller to use
        else:
            return {"error": "API returned an unsuccessful status."}

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def get_country_code(country_name):
    """
    Convert a country name to its ISO 3166-1 alpha-2 country code.
    """
    try:
        return pycountry.countries.lookup(country_name).alpha_2
    except LookupError:
        return None