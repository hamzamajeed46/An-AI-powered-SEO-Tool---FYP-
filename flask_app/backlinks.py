import requests
from langchain_groq import ChatGroq
from markdown import markdown
from config import Config
from flask import session
from pymongo import MongoClient, DESCENDING
import os
from datetime import datetime

# MongoDB setup
def get_db_connection():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['seotool']
    return db

def fetch_backlinks(input_web):
    """
    Fetch backlinks data from Ahrefs API or fallback to local MongoDB if API fails.

    Args:
        input_web (str): The website URL to analyze.

    Returns:
        dict: Backlinks data or an error message.
    """
    db = get_db_connection()
    url = "https://ahrefs2.p.rapidapi.com/backlinks"
    querystring = {"url": input_web, "mode": "subdomains"}

    headers = {
        "x-rapidapi-key": os.getenv('API_KEY4'),
        "x-rapidapi-host": "ahrefs2.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            backlinks_data = response.json()

            # If user is logged in, insert into MongoDB
            if 'email' in session:
                db.backlinks.insert_one({
                    "email": session['email'],
                    "url"  : input_web,
                    "backlinks": backlinks_data,
                    "date": datetime.utcnow().strftime('%Y-%m-%d')
                })

            return backlinks_data

        else:
            print("API failed, trying to fetch from database...")

            # Try finding recent data in MongoDB
            result = db.backlinks.find_one(
                {"backlinks.url": input_web},
                sort=[("date", DESCENDING)]
            )

            if result:
                return result['backlinks']
            else:
                return {"error": "API failed and no cached data available in database."}

    except Exception as e:
        print("Error fetching backlinks:", e)
        return {"error": str(e)}
    

# Function to generate SEO recommendations using ChatGroq
def generate_seo_recommendations(backlinks_data):
    """
    Generate SEO recommendations if not already present for the latest backlinks entry.

    Args:
        backlinks_data (dict): Backlinks data to analyze.

    Returns:
        str: SEO insights and recommendations.
    """

    # Initialize the ChatGroq LLM
    llm = ChatGroq(
        temperature=0.5,
        groq_api_key=Config.LLM_API,
        model_name="deepseek-r1-distill-llama-70b"
    )

    prompt = (
        "Act as seo expert and Analyze the following website backlinks data and provide SEO recommendations "
        "and acquisition strategies for the client to improve their performance/backlinks of website. "
        "Backlinks Data: \n\n"
        f"{backlinks_data}"
        "\nDirectly provide specific and actionable recommendations only for the client in detail."
    )

    response = llm.invoke(prompt)
    seo_recommendations = markdown(response.content)
    
    if 'user_id' in session and 'username' in session:
        db = get_db_connection()
        backlinks_collection = db['backlinks']

        # Find most recent document for this user
        latest_data = backlinks_collection.find_one(
            {"email": session['email'], "url": backlinks_data.get("url")},
            sort=[("date", -1)]
        )

        if latest_data and 'recommendations' in latest_data:
            print("Recommendations already exist. Skipping update.")
        else:
            # Update document
            backlinks_collection.update_one(
                {"_id": latest_data['_id']},
                {"$set": {"recommendations": seo_recommendations}}
            )
            print("Recommendations added successfully.")

    return seo_recommendations

# Function to generate SEO insights using ChatGroq
def generate_seo_insights(backlinks_data):
    """
    Generate SEO insights if not already present for the latest backlinks entry.

    Args:
        backlinks_data (dict): Backlinks data to analyze.

    Returns:
        str: SEO insights and recommendations.
    """

    # Initialize the ChatGroq LLM
    llm = ChatGroq(
        temperature=0,
        groq_api_key=Config.LLM_API,
        model_name="llama-3.3-70b-versatile"
    )

    prompt = (
        "Analyze the following website backlinks data and provide SEO insights. "
        "Backlinks Data: \n\n"
        f"{backlinks_data}"
    )

    response = llm.invoke(prompt)
    seo_insights = markdown(response.content)
    
    if 'user_id' in session and 'username' in session:
        db = get_db_connection()
        backlinks_collection = db['backlinks']

        # Find most recent document for this user
        latest_data = backlinks_collection.find_one(
            {"email": session['email'], "url": backlinks_data.get("url")},
            sort=[("date", -1)]
        )

        if latest_data and 'insights' in latest_data:
            print("Insights already exist. Skipping update.")
        else:
            # Update document
            backlinks_collection.update_one(
                {"_id": latest_data['_id']},
                {"$set": {"insights": seo_insights}}
            )
            print("Insights added successfully.")

    return seo_insights
