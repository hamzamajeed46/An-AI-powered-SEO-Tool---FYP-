from markdown import markdown
from flask import session
from langchain_groq import ChatGroq
from config import Config
from backlinks import get_db_connection  
from traffic import get_traffic_history

db = get_db_connection()
traffic_collection = db["traffic"]

def fetch_traffic_data(website):
    """Fetch traffic history and raw data for a given website."""
    history, data = get_traffic_history(website)
    return history, data

def store_recommendations(email, website, recommendations):
    """
    Store SEO recommendations for a website in the most recent document 
    in the 'traffic' collection based on the email and website URL.
    """
    # Find the most recent document for the specified email and website URL
    latest_doc = traffic_collection.find_one(
        {"email": email, "url": website},
        sort=[("_id", -1)]  # Sort by _id in descending order to get the latest document
    )

    if latest_doc:
        # Update the most recent document with the SEO recommendations
        traffic_collection.update_one(
            {"_id": latest_doc["_id"]},  # Find the document by its _id
            {"$set": {"recommendations": recommendations}}  # Set the recommendations field
        )
    else:
        # If no document exists, you could handle this case (e.g., create a new document)
        print(f"No document found for email: {email} and website: {website}")

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
        groq_api_key=os.getenv('LLM_API'),
        model_name="llama-3.3-70b-versatile"
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
