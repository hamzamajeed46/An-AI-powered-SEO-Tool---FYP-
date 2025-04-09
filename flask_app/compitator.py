from googlesearch import search
import pycountry
from backlinks import fetch_backlinks
from langchain_groq import ChatGroq
import markdown
from config import Config

def compare_backlinks(main_website, competitor_website):
    """
    Compare backlinks data between two websites and generate recommendations using Groq LLM.
    """
    main_backlinks = fetch_backlinks(main_website)
    competitor_backlinks = fetch_backlinks(competitor_website)

    # Check if any error occurred
    if "error" in main_backlinks:
        return {"error": f"Error fetching data for {main_website}: {main_backlinks['error']}"}
    if "error" in competitor_backlinks:
        return {"error": f"Error fetching data for {competitor_website}: {competitor_backlinks['error']}"}

    # Generate recommendations using Groq LLM
    recommendations = generate_groq_recommendations(main_backlinks, competitor_backlinks)

    return {
        "main_backlinks": main_backlinks,
        "competitor_backlinks": competitor_backlinks,
        "recommendations": recommendations
    }

def generate_groq_recommendations(main_backlinks, competitor_backlinks):
    """
    Use Groq LLM to generate SEO recommendations based on backlink comparison.
    """
    # Initialize the ChatGroq LLM
    llm = ChatGroq(
        temperature=0,
        groq_api_key=Config.LLM_API,
        model_name="llama-3.3-70b-versatile"
    )

    # Create the prompt
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

    return search(keyword, region=country_code, num_results=min(num_results, 100))
