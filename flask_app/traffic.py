import requests
from langchain_groq import ChatGroq
from markdown import markdown
from config import Config

# API Details
API_URL = "https://ahrefs1.p.rapidapi.com/v1/website-traffic-checker"
HEADERS = {
    "x-rapidapi-key": Config.API_KEY,
    "x-rapidapi-host": "ahrefs1.p.rapidapi.com"
}

def get_traffic_history(website):
    """Fetches traffic history for the given website."""
    query_params = {"url": website, "mode": "subdomains"}
    response = requests.get(API_URL, headers=HEADERS, params=query_params)

    if response.status_code != 200:
        return None, "API Error: Unable to fetch data"

    data = response.json()
    
    # Extract traffic history (format: {"10": 74, "11": 53, ...})
    traffic_history = {item["date"][5:7]: item["organic"] for item in data.get("traffic_history", [])}

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

