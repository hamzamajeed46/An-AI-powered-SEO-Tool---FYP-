import json
import os
import http.client
from flask import session
from langchain_groq import ChatGroq
from markdown import markdown
from config import Config
from backlinks import get_db_connection  # Assuming you have this function to get the DB connection

# API Details
API_URL = "https://ahrefs1.p.rapidapi.com/traffic"
HEADERS = {
    "x-rapidapi-key": os.getenv('API_KEY3'),
    "x-rapidapi-host": "ahrefs1.p.rapidapi.com"
}


def get_traffic_history(website):
    """
    Fetch the traffic history data from the API.
    Insert it into the 'traffic' collection if the user is logged in.
    """
    try:
        conn = http.client.HTTPSConnection("ahrefs2.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': os.getenv("API_KEY3"),
            'x-rapidapi-host': "ahrefs2.p.rapidapi.com"
        }
        
        conn.request("GET", f"/traffic?url={website}&mode=subdomains", headers=headers)
        res = conn.getresponse()
        data = res.read()
        data = json.loads(data)

        # Extract traffic history
        traffic_history = {item["date"][5:7]: item["organic"] for item in data.get("traffic_history", [])}
        
        # Insert into MongoDB if user logged in
        if res.status == 200 and "email" in session:
            db = get_db_connection()
            traffic_doc = {
                "email": session["email"],
                "url": website,
                "traffic": data  # Save the full API response
            }
            db.traffic.insert_one(traffic_doc)

        return traffic_history, data  # Return both traffic_history and full data

    except Exception as e:
        print(str(e))
        return {}, {"error": f"Failed to fetch traffic history: {str(e)}"}



def traffic_insights(traffic_data):
    """
    Analyze the traffic data and generate actionable SEO insights,
    then store recommendations in the most recent traffic document for the current user and URL.
    """
    try:
        db = get_db_connection()

        # Initialize the ChatGroq LLM
        llm = ChatGroq(
            temperature=0,
            groq_api_key=Config.LLM_API,
            model_name="deepseek-r1-distill-llama-70b"
        )

        # Create the prompt
        prompt = (
            "Analyze the following website traffic history data and provide SEO insights "
            "and acquisition strategies for the client to improve their website's performance.\n\n"
            f"Traffic Data:\n{traffic_data}\n"
            "Provide specific and actionable recommendations only for the client in detail."
        )

        # Invoke the LLM
        response = llm.invoke(prompt)
        
        if response:
            recommendations_html = markdown(response.content)

            # If user is logged in, update the most recent traffic document for this URL
            if "email" in session:
    # Find the most recent document for the current user and URL
                latest_document = db.traffic.find_one(
                    {"email": session["email"], "url": traffic_data.get("url")},
                    sort=[("_id", -1)]  # Sort by _id in descending order to get the most recent one
                )

                if latest_document:
                    # Update the most recent document with the recommendations
                    db.traffic.update_one(
                        {"_id": latest_document["_id"]},  # Match by the _id of the latest document
                        {"$set": {"recommendations": recommendations_html}}  # Set the recommendations
                    )

            return recommendations_html
        else:
            return "No recommendations provided."
        
    except Exception as e:
        return f"Failed to generate traffic insights: {str(e)}"

