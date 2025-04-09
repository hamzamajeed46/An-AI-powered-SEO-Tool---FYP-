import json
from langchain_groq import ChatGroq
from markdown import markdown
import os
from config import Config
import http.client

# API Details
API_URL = "https://ahrefs2.p.rapidapi.com/traffic"
HEADERS = {
    "x-rapidapi-key": os.getenv('API_KEY1'),
    "x-rapidapi-host": "ahrefs1.p.rapidapi.com"
}

def get_traffic_history(website):
    

    conn = http.client.HTTPSConnection("ahrefs1.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': os.getenv("API_KEY"),
        'x-rapidapi-host': "ahrefs1.p.rapidapi.com"
    }

    conn.request("GET", f"/v1/website-traffic-checker?url={website}&mode=subdomains", headers=headers)

    res = conn.getresponse()
    data = res.read()

    data = json.loads(data)
    
    # Extract traffic history (format: {"10": 74, "11": 53, ...})
    traffic_history = {item["date"][5:7]: item["organic"] for item in data.get("traffic_history", [])}
    print(traffic_history,data)  # Debugging line to check the traffic history
    return traffic_history, data  # Returning both traffic history and full data


def traffic_insights(traffic_data):
    """
    Analyze the backlinks data and generate actionable SEO recommendations.

    Args:
        backlinks_data (dict): Backlinks data to analyze.

    Returns:
        str: SEO insights and recommendations.
    """
    # Initialize the ChatGroq LLM
    llm = ChatGroq(
        temperature=0,
        groq_api_key= Config.LLM_API,
        model_name="llama-3.3-70b-versatile"
    )

    # Create the prompt
    prompt = (
        "Analyze the following website traffic history data and provide SEO insights "
        "and aquisition strategies for the client to improve their performance/backlinks of website."
        "Backlinks Data: \n\n"
        f"{traffic_data}"
        "\nProvide specific and actionable recommendations only for the client."
    )

    # Invoke the LLM and get the response
    response = llm.invoke(prompt)
    return markdown(response.content)  # Convert the response to Markdown

