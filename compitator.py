from googlesearch import search
import pycountry
from backlinks import fetch_backlinks, get_db_connection
from langchain_groq import ChatGroq
import markdown
from config import Config
from flask import session
from pymongo import MongoClient
from datetime import datetime

def store_competitor_data(keyword, comp_data, country):
    """
    Store backlinks data for the competitor in the 'competitors' collection,
    including a timestamp of when the data is added/updated.
    """
    try:
        # Create a document with keyword, country, competitors data, and date
        document = {
            "keyword": keyword,
            "country": country,
            "competitors": comp_data,
            "date": datetime.utcnow()  # Add current UTC timestamp
        }

        # Insert the document
        competitors_collection.insert_one(document)

        return {"status": "success", "message": "Data inserted successfully."}
    
    except Exception as e:
        return {"error": str(e)}  # Return an error message in case of failure


# MongoDB client setup
client = MongoClient('mongodb://localhost:27017/')
db = client["seotool"] 
backlinks_collection = db["backlinks"]
competitors_collection = db["competitors"]

def compare_backlinks(main_website, competitor_website):
    """
    Compare backlinks data between two websites and generate recommendations using Groq LLM.
    """
    # Fetch backlinks for both the main website (user) and the competitor
    main_backlinks = fetch_backlinks(main_website)
    competitor_backlinks = fetch_backlinks(competitor_website)

    # Check if any error occurred while fetching backlinks data
    if "error" in main_backlinks:
        return {"error": f"Error fetching data for {main_website}: {main_backlinks['error']}"}
    if "error" in competitor_backlinks:
        return {"error": f"Error fetching data for {competitor_website}: {competitor_backlinks['error']}"}

    
    # Generate recommendations using Groq LLM
    recommendations = generate_groq_recommendations(main_backlinks, competitor_backlinks)

    # Store the recommendations in the user's document
    store_recommendations(main_website, recommendations)

    return {
        "main_backlinks": main_backlinks,
        "competitor_backlinks": competitor_backlinks,
        "recommendations": recommendations
    }

def store_backlinks_data(website, backlinks_data):
    """
    Store backlinks data in the 'backlinks' collection for the user's website.
    """
    backlinks_collection.update_one(
        {"email": session.get("email"), "url": website},
        {"$set": {"backlinks_data": backlinks_data}},
        upsert=True  # Insert a new document if it doesn't exist
    )


def store_competitor_data(keyword, comp_data, country):
    """
    Store backlinks data for the competitor in the 'competitors' collection,
    including a timestamp of when the data is added/updated.
    """
    try:
        # Create a document with keyword, country, competitors data, and date
        document = {
            "keyword": keyword,
            "country": country,
            "competitors": comp_data,
            "date": datetime.utcnow()  # Add current UTC timestamp
        }

        # Insert the document
        competitors_collection.insert_one(document)

        return {"status": "success", "message": "Data inserted successfully."}
    
    except Exception as e:
        return {"error": str(e)}

def store_recommendations(website, recommendations):
    """
    Store SEO recommendations in the user's document in the 'backlinks' collection.
    """
    backlinks_collection.update_one(
        {"email": session.get("email"), "url": website},
        {"$set": {"recommendations": recommendations}},
        upsert=True  # Insert a new document if it doesn't exist
    )

def generate_groq_recommendations(main_backlinks, competitor_backlinks):
    """
    Use Groq LLM to generate SEO recommendations based on backlink comparison.
    """
    # Initialize the ChatGroq LLM
    llm = ChatGroq(
        temperature=0,
        groq_api_key=os.getenv('LLM_API'),
        model_name="llama-3.3-70b-versatile"
    )

    # Create the prompt for Groq LLM
    prompt = (
        "Analyze the backlinks data of two websites and provide SEO recommendations "
        "to improve the client's backlink strategy and outperform the competitor."
        "\n\nClient's Website Backlink Data:\n"
        f"{main_backlinks}\n\n"
        "Competitor's Website Backlink Data:\n"
        f"{competitor_backlinks}\n\n"
        "Provide specific and actionable recommendations for the client, "
        "focusing on high-authority backlinks, domain diversity, and dofollow links."
    )

    # Invoke the LLM and get the response
    response = llm.invoke(prompt)
    return markdown.markdown(response.content)  # Convert the response to Markdown

def get_country_code(country_name):
    """
    Convert a country name to its ISO 3166-1 alpha-2 country code.
    """
    try:
        return pycountry.countries.lookup(country_name).alpha_2
    except LookupError:
        return None

def find_compitators(keyword, country="us", num_results=10):
    """
    Find competitor websites based on a keyword and country.
    """
    # Convert country name to country code
    country_code = get_country_code(country)
    if not country_code:
        return {"error": "Invalid country selected."}

    comp_data = search(keyword, region=country_code, num_results=min(num_results, 100))
    store_competitor_data(keyword, comp_data, country)
    return comp_data
