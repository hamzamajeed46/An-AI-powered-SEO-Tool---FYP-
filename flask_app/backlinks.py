import requests
from langchain_groq import ChatGroq
from markdown import markdown
from config import Config 

# Function to call the Ahrefs API and fetch backlinks data
def fetch_backlinks(input_web):
    """
    Fetch backlinks data from Ahrefs API.

    Args:
        input_web (str): The website URL to analyze.

    Returns:
        dict: Backlinks data or an error message.
    """
    url = "https://ahrefs2.p.rapidapi.com/backlinks"
    querystring = {"url": input_web, "mode": "subdomains"}

    headers = {
        "x-rapidapi-key": Config.API_KEY,
        "x-rapidapi-host": "ahrefs2.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        return response.json()  # Return the JSON response
    else:
        return {"error": f"Failed to fetch data. Status Code: {response.status_code}"}

# Function to generate SEO recommendations using ChatGroq
def generate_seo_recommendations(backlinks_data):
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
        groq_api_key=Config.LLM_API,
        model_name="llama-3.3-70b-versatile"
    )

    # Create the prompt
    prompt = (
        "Analyze the following website backlinks data and provide SEO recommendations "
        "and aquisition strategies for the client to improve their performance/backlinks of website."
        "Backlinks Data: \n\n"
        f"{backlinks_data}"
        "\nProvide specific and actionable recommendations only for the client."
    )

    # Invoke the LLM and get the response
    response = llm.invoke(prompt)
    return markdown(response.content)  # Convert the response to Markdown

def generate_seo_insights(backlinks_data):
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
        groq_api_key=Config.LLM_API,
        model_name="llama-3.3-70b-versatile"
    )

    # Create the prompt
    prompt = (
        "Analyze the following website backlinks data and provide SEO insights "
        "Backlinks Data: \n\n"
        f"{backlinks_data}"
        
    )

    # Invoke the LLM and get the response
    response = llm.invoke(prompt)
    return markdown(response.content)  # Convert the response to Markdown
