import requests
from bs4 import BeautifulSoup
import re
import markdown
from langchain_groq import ChatGroq

# Initialize the ChatGroq LLM
llm = ChatGroq(
    temperature=0,
    groq_api_key='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',
    model_name="llama3-70b-8192"
)

# Function to fetch metadata from a URL
def fetch_metadata(url):
    try:
        response = requests.get(url, timeout=25)
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
def generate_recommendations(client_metadata, competitor_metadata=None):
    try:
        # Prepare a prompt for the LLM
        prompt = (
            "Analyze the following website metadata and provide SEO recommendations "
            "for the client to improve their website's performance compared to their competitor."
            "\n\n"
            f"Client Metadata:\n"
            f"Title: {client_metadata['title']}\n"
            f"Description: {client_metadata['description']}\n"
            f"Canonical URL: {client_metadata['canonical']}\n"
            f"Favicon: {client_metadata['favicon']}\n"
            f"H1 Tag: {client_metadata['h1']}\n"
        )
        
        if competitor_metadata:
            prompt += (
                "\nCompetitor Metadata:\n"
                f"Title: {competitor_metadata['title']}\n"
                f"Description: {competitor_metadata['description']}\n"
                f"Canonical URL: {competitor_metadata['canonical']}\n"
                f"Favicon: {competitor_metadata['favicon']}\n"
                f"H1 Tag: {competitor_metadata['h1']}\n"
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
        response = requests.get(url, timeout=15)
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
        
        return keyword_data
    except Exception as e:
        return {"error": f"Failed to analyze {url}: {str(e)}"}
