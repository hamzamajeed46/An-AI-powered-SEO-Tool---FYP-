# compare_traffic.py
import os
from traffic import get_traffic_history
from langchain_groq import ChatGroq
from markdown import markdown
from flask import session
from config import Config
from backlinks import get_db_connection  

db = get_db_connection()
traffic_collection = db["traffic"]

def fetch_traffic_data(website):
    """Fetch traffic history and raw data for a given website."""
    history, data = get_traffic_history(website)
    return history, data

def store_recommendations(email, website, recommendations):
    """
    Store SEO recommendations for a website in the existing document in the 'traffic' collection.
    """
    # Update the most recent document with the recommendations for the specific email and website URL
    traffic_collection.update_one(
        {"email": email, "url": website},
        {"$set": {"recommendations": recommendations}},
        sort=[("_id", -1)]  # Ensure the most recent document is updated
    )

def generate_llm_comparison_insights(data1, data2, website1, website2):
    """
    Uses Groq LLM to generate insights and recommendations for two websites.

    Args:
        data1 (dict): Traffic data for website1
        data2 (dict): Traffic data for website2
        website1 (str): First website
        website2 (str): Second website
        email (str): The user's email to associate the data with

    Returns:
        str: Insights and SEO recommendations from the LLM
    """
    # Setup LLM
    llm = ChatGroq(
        temperature=0,
        groq_api_key=Config.LLM_API,
        model_name="deepseek-r1-distill-llama-70b"
    )

    prompt = f"""Act as seo expert and you will be telling below things to a non seo expert.
    
You are given the website traffic data for two websites. Your task is to:
1. Compare their monthly traffic, costs, top countries, and keyword performance.
2. Highlight the strengths and weaknesses of each website.
3. Provide clear, specific and actionable SEO recommendations to help **{website1}** improve based on the competitor **{website2}**.

Use the data below:

Website 1: {website1}
Data:
{data1}

Website 2: {website2}
Data:
{data2}

Give a detailed analysis and recommendations for **{website1}** to improve its performance based on the comparison with **{website2}**
"""

    response = llm.invoke(prompt)
    recommendations = markdown(response.content)  # Convert response to markdown
    if 'email' in session:
        email = session['email']
        # Store the recommendations in the database for the user and website
    store_recommendations(email, website1, recommendations)

    return recommendations  # Return the recommendations for further use or response
