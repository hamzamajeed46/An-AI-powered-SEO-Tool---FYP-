import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from flask import session
import markdown
from langchain_groq import ChatGroq
from config import Config 
from backlinks import get_db_connection 

# Initialize the ChatGroq LLM


def fetch_metadata(url, keyword=None):
    try:
        db = get_db_connection()  # Get the database connection

        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        response = requests.get(url, timeout=35)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        body_text = soup.get_text(separator=" ").lower()
        words = body_text.split()
        total_words = len(words)

        # Extracting metadata
        title = soup.title.string if soup.title else "No Title Found"
        description = soup.find("meta", attrs={"name": "description"})
        description = description["content"] if description else "No Description Found"
        canonical = soup.find("link", attrs={"rel": "canonical"})
        canonical = canonical["href"] if canonical else "No Canonical URL Found"
        favicon = soup.find("link", attrs={"rel": "icon"})
        favicon = "Exists" if favicon else "Missing"
        h1 = soup.find("h1")
        h1 = h1.get_text(strip=True) if h1 else "No H1 Tag Found"
        
        metadata = {
            "title": title,
            "description": description,
            "canonical": canonical,
            "favicon": favicon,
            "h1": h1,
            "url": url  # Add URL also in metadata
        }

        keyword_data = {}
        if keyword:
            # Analyze keyword
            keywords = [keyword.lower()] + keyword.lower().split()
            for word in keywords:
                count = len(re.findall(rf"\b{re.escape(word)}\b", body_text))
                density = round((count / total_words) * 100, 2) if total_words > 0 else 0
                keyword_data[word] = {"count": count, "density": density}

        # If user logged in, insert into 'metadata' collection
        if 'email' in session:
            doc = {
                "email": session['email'],
                "title": title,
                "description": description,
                "canonical": canonical,
                "favicon": favicon,
                "h1": h1,
                "url": url,
                "date": datetime.utcnow().strftime('%Y-%m-%d')
            }
            if keyword:
                doc['keyword_data'] = keyword_data
                

            db.metadata.insert_one(doc)

        if keyword:
            return metadata, keyword_data, body_text
        
        return metadata
        
    except Exception as e:
        return {"error": f"Failed to fetch metadata: {str(e)}"}


def metadata_recommendations(client_metadata):
    try:
        llm = ChatGroq(
            temperature=0,
            groq_api_key= os.getenv('LLM_API'),
            model_name="llama-3.3-70b-versatile"
        )
        db = get_db_connection()

        # Prepare a prompt for the LLM
        prompt = (
            "Analyze the following website metadata and provide SEO recommendations "
            "for the client to improve their website's performance.\n"
            f"Client Metadata:\n{client_metadata}\n"
            "Provide specific and actionable recommendations only for the client."
        )

        # Invoke the LLM
        response = llm.invoke(prompt)
        
        if response:
            recommendations_html = markdown.markdown(response.content)

            # If user is logged in, update the most recent metadata document
            db.metadata.update_one(
                {"email:": session["email"]},
                {"$set": {"recommendations": recommendations_html}},
                sort=[("_id", -1)]  # Sort by latest inserted document
            )

            return recommendations_html
        else:
            return "No recommendations provided."
        
    except Exception as e:
        return f"Failed to generate recommendations: {str(e)}"