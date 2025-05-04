import requests
from config import Config
import os
from datetime import datetime
import pycountry
from langchain_groq import ChatGroq
from backlinks import beautify_markdown_to_html, get_db_connection  

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
        "x-rapidapi-key": os.getenv('API_KEY4'),  # Fetch API key from environment variable
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

def generate_blog_from_keyword(prompt, keyword):
    llm = ChatGroq(
    temperature=0,
    groq_api_key= Config.LLM_API,
    model_name="llama-3.3-70b-versatile"
    )
    # Call the LLM API (similar to your metadata_recommendations function)
    try:
        response = llm.invoke(prompt)
        if response:
            return beautify_markdown_to_html(response.content, title="Blog for Keyword: " + keyword)
        else:
            return "No content generated."
    except Exception as e:
        return f"Error: {str(e)}"



def fetch_unsplash_image(keyword):
    access_key = os.getenv("access_key")
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": keyword,
        "per_page": 1,
        "orientation": "landscape",
        "client_id": access_key
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            return data["results"][0]["urls"]["regular"]
    return None
