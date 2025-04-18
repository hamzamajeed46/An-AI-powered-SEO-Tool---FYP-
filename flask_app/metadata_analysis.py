import requests
from bs4 import BeautifulSoup
import re
import markdown
from langchain_groq import ChatGroq
from config import Config 

# Initialize the ChatGroq LLM
llm = ChatGroq(
    temperature=0,
    groq_api_key= Config.LLM_API,
    model_name="llama3-70b-8192"
)

# Function to fetch metadata from a URL
def fetch_metadata(url):
    try:
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        response = requests.get(url, timeout=35)
        soup = BeautifulSoup(response.text, 'html.parser')
        
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
        
        return {
            "title": title,
            "description": description,
            "canonical": canonical,
            "favicon": favicon,
            "h1": h1
        }
    except Exception as e:
        return {"error": f"Failed to fetch metadata: {str(e)}"}

# Function to generate recommendations using the LLM
def metadata_recommendations(client_metadata):
    try:    
        # Prepare a prompt for the LLM
        prompt = (
            "Analyze the following website metadata and provide SEO recommendations "
            "for the client to improve their website's performance"
            "\n"
            f"Client Metadata:\n"
            f"{client_metadata}"
            
        )

        prompt += "\nProvide specific and actionable recommendations only for the client."

        # Invoke the LLM
        response = llm.invoke(prompt)
        
        if response:
            # Convert Markdown to HTML
            return markdown.markdown(response.content)
        else:
            return "No recommendations provided."
    except Exception as e:
        return f"Failed to generate recommendations: {str(e)}"

# Function to analyze keyword usage in the website's body text
def analyze_keywords(url, keyword):
    try:
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract body text
        body_text = soup.get_text(separator=" ").lower()
        words = body_text.split()
        total_words = len(words)
        
        # Analyze keyword
        keyword_data = {}
        keywords = [keyword.lower()] + keyword.lower().split()
        
        for word in keywords:
            count = len(re.findall(rf"\b{re.escape(word)}\b", body_text))
            density = round((count / total_words) * 100, 2) if total_words > 0 else 0
            keyword_data[word] = {"count": count, "density": density}
        
        return keyword_data,body_text
    except Exception as e:
        return {"error": f"Failed to analyze {url}: {str(e)}"}
