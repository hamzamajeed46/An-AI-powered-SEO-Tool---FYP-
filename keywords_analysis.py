import requests
from config import Config
import os
from datetime import datetime
import pycountry
from langchain_groq import ChatGroq
from backlinks import beautify_markdown_to_html, get_db_connection  

ChatGroq.model_rebuild()

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
    try:
        url = "https://google-keyword-insight1.p.rapidapi.com/topkeys/"
        country = country.upper()
        querystring = {"keyword":keyword,"location":country,"lang":"en"}

        headers = {
            "x-rapidapi-key": os.getenv('API_KEY3'),
            "x-rapidapi-host": "google-keyword-insight1.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        data = response.json()

        if data:
            suggestions = {
                "keyword": keyword,
                "country": country,
                "Ideas": data,
                "date": datetime.utcnow()  # Add current UTC timestamp
            }

            # Insert the suggestions data into the 'keywords' collection
            keywords_collection.insert_one(suggestions)

            return suggestions  # Return the data for the caller to use
        else:
            return {"error": "API returned an unsuccessful status."}

    except Exception as e:
        return f"Error: {str(e)}"


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
    groq_api_key= os.getenv("LLM_API"),
    model_name="meta-llama/llama-4-scout-17b-16e-instruct"
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

def generate_image_from_keyword(keyword):
    try:
        url = "https://ai-text-to-image-generator-flux-free-api.p.rapidapi.com/aaaaaaaaaaaaaaaaaiimagegenerator/quick.php"

        payload = {
            "prompt": f"An image for blog post about {keyword}",
            "style_id": 2,
            "size": "1-1"
        }
        headers = {
            "x-rapidapi-key": os.getenv('API_KEY4'),
            "x-rapidapi-host": "ai-text-to-image-generator-flux-free-api.p.rapidapi.com",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        response = response.json()


        if response['final_result']:
            return response['final_result'][0]['origin'], response['final_result'][1]['origin']
        else:
            return None, None
    except Exception as e:
        return f"Error: {str(e)}"