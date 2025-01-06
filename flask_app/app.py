from flask import Flask, render_template, request
import requests
from langchain_groq import ChatGroq
from markdown import markdown

app = Flask(__name__)

# Home route to render the input form
@app.route('/')
def home():
    return render_template('backlinks.html')

# Route to handle the API call and display results
@app.route('/get_backlinks', methods=['POST'])
def get_backlinks():
    input_web = request.form['website']  # Get the website from the form
    url = "https://ahrefs2.p.rapidapi.com/backlinks"

    querystring = {"url": input_web, "mode": "subdomains"}

    headers = {
        "x-rapidapi-key": "85e7d0841amshe3a29d2229bb909p17f5ccjsnefcb401c476a",
        "x-rapidapi-host": "ahrefs2.p.rapidapi.com"
    }

    # Call the API
    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()  # Parse the JSON response
        groq_api_key = "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"
        recommendations = generate_seo_recommendations(data, groq_api_key)
        return render_template('results.html', data=data, recommendations=recommendations)  # Pass data to template
    else:
        error_message = f"Failed to fetch data. Status Code: {response.status_code}"
        return render_template('results.html', error=error_message)

@app.route('/get_backlinks', methods=['POST'])
def generate_seo_recommendations(backlinks_data, groq_api_key):
    """
    Analyzes the backlinks data and generates actionable SEO recommendations using ChatGroq LLM.

    Args:
        backlinks_data (dict): Backlinks data to analyze.
        groq_api_key (str): API key for the ChatGroq LLM.

    Returns:
        str: SEO insights and recommendations.
    """
    # Initialize the ChatGroq LLM
    llm = ChatGroq(
        temperature=0,
        groq_api_key=groq_api_key,
        model_name="llama3-70b-8192"
    )

    # Create the prompt
    prompt = (
        "Analyze the following website backlinks data and provide SEO insights "
        "for the client to improve their performance/backlinks of website."
        "Backlinks Data: \n\n"
        f"{backlinks_data}"
        "\nProvide specific and actionable recommendations only for the client."
    )

    # Invoke the LLM and get the response
    response = llm.invoke(prompt)
    response = markdown(response.content)
    return response

if __name__ == '__main__':
    app.run(debug=True)
