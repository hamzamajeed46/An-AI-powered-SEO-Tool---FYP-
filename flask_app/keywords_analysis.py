import requests
import os  # Added to access environment variables

def fetch_keyword_suggestions(keyword, search_engine="google", country="us"):
    """
    Fetch keyword suggestions from the API.

    Args:
        keyword (str): The main keyword to analyze.
        search_engine (str): The search engine to use (default: "google").
        country (str): The country code for the search (default: "us").

    Returns:
        dict: A dictionary containing keyword suggestions and related questions.
    """
    url = "https://ahrefs2.p.rapidapi.com/keyword_suggestions"
    querystring = {"keyword": keyword, "se": search_engine, "country": country}

    headers = {
        "x-rapidapi-key": "85e7d0841amshe3a29d2229bb909p17f5ccjsnefcb401c476a",  # Fetch API key from environment variable
        "x-rapidapi-host": "ahrefs2.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx
        data = response.json()

        if data.get("status") == "success":
            return {
                "Ideas": data.get("Ideas", []),
                "Questions": data.get("Questions", [])
            }
        else:
            return {"error": "API returned an unsuccessful status."}

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
