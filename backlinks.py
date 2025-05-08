import requests
from langchain_groq import ChatGroq
from markdown import markdown
from config import Config
from flask import session
from pymongo import MongoClient, DESCENDING
import os
from datetime import datetime
from bs4 import BeautifulSoup


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
        "x-rapidapi-key": os.getenv('API_KEY1'),
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
        model_name="llama-3.3-70b-versatile"
    )

    prompt = (
        "Act as seo expert and Analyze the following website backlinks data and provide SEO recommendations "
        "and acquisition strategies for the client to improve their performance/backlinks of website. "
        "Backlinks Data: \n\n"
        f"{backlinks_data}"
        "\nDirectly provide specific and actionable recommendations only for the client in detail."
    )

    response = llm.invoke(prompt)
    seo_recommendations = beautify_markdown_to_html(response.content)
    
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
    seo_insights = beautify_markdown_to_html(response.content, title="Insights")
    
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


def beautify_markdown_to_html(content, title="Recommendations"):
    """
    Converts Markdown content into beautifully formatted HTML with a modern, glassmorphism-inspired UI and advanced inline styling.
    If a title is provided, it is rendered as an H3 at the top.
    """
    raw_html = markdown(content)
    soup = BeautifulSoup(raw_html, 'html.parser')

    # Apply inline styles to each tag
    styles = {
        'h1': "font-size: 2.2rem; font-weight: 800; color: #1a202c; margin-bottom: 18px; letter-spacing: 0.5px;",
        'h2': "font-size: 1.7rem; font-weight: 700; color: #2563eb; margin-bottom: 15px; letter-spacing: 0.3px;",
        'h3': "font-size: 1.3rem; font-weight: 600; color: #2563eb; margin-bottom: 12px;",
        'p': "font-size: 1.08rem; color: #374151; margin: 14px 0; line-height: 1.8;",
        'ul': "margin: 14px 0 14px 24px; padding-left: 0.7rem; background: #f7faff; border-radius: 0.8rem; padding: 12px 18px;",
        'ol': "margin: 14px 0 14px 24px; padding-left: 0.7rem; background: #f7faff; border-radius: 0.8rem; padding: 12px 18px;",
        'li': "margin-bottom: 8px; font-size: 1.08rem; color: #374151; position: relative;",
        'a': "color: #2563eb; text-decoration: none; border-bottom: 1.5px dashed #2563eb33; transition: color 0.2s;",
        'blockquote': "border-left: 4px solid #3b82f6; background: #f0f4ff; padding: 12px 22px; font-style: italic; color: #334155; margin: 22px 0; border-radius: 0.7rem;",
        'code': "background: #f3f4f6; padding: 2px 8px; border-radius: 5px; font-family: 'JetBrains Mono', 'Courier New', monospace; font-size: 1rem;",
        'pre': "background: #1e293b; color: #e2e8f0; padding: 18px; border-radius: 10px; overflow-x: auto; font-size: 1rem; margin: 18px 0;"
    }

    for tag, style in styles.items():
        for element in soup.find_all(tag):
            existing = element.get("style", "")
            element["style"] = f"{existing} {style}".strip()

    # Add hover effect to links
    for element in soup.find_all('a'):
        element['onmouseover'] = "this.style.color='#0e4fc1'"
        element['onmouseout'] = "this.style.color='#2563eb'"

    html_content = str(soup)

    # Add the title as h3 if provided and not empty
    title_html = ""
    if title:
        title_html = f'<h3 style="text-align: center; font-size: 1.5rem; font-weight: 800; color: #645dec; margin-bottom: 24px; letter-spacing: 0.5px;">{title}</h3>'

    beautified_html = f"""
    <div style=\"font-family: 'Inter', 'Segoe UI', Arial, sans-serif; background: rgba(247,249,252,0.85); padding: 40px 0;\">
      <div style=\"max-width: 900px; margin: auto; background: rgba(255,255,255,0.78); border-radius: 22px; box-shadow: 0 8px 32px rgba(0, 123, 255, 0.10); padding: 48px 30px 38px 30px; backdrop-filter: blur(8px); position: relative; overflow: hidden; animation: fadeInModern 1.2s cubic-bezier(.23,1,.32,1);\">
        <div style=\"position: absolute; left: 0; top: 0; width: 100%; height: 8px; background: linear-gradient(90deg, #00c6ff 0%, #007bff 100%); border-radius: 22px 22px 0 0;\"></div>
        {title_html}
        {html_content}
      </div>
    </div>
    <style>
      @keyframes fadeInModern {{
        0% {{ opacity: 0; transform: translateY(40px) scale(0.98); }}
        100% {{ opacity: 1; transform: translateY(0) scale(1); }}
      }}
    </style>
    """
    return beautified_html