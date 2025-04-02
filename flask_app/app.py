from flask import Flask, render_template, request, redirect, url_for
from flask import session
import zlib
import base64
import json
import pycountry
from compitator import find_compitators
from backlinks import fetch_backlinks, generate_seo_recommendations, generate_seo_insights
from metadata_analysis import fetch_metadata, metadata_recommendations, analyze_keywords
from traffic import get_traffic_history, traffic_insights
from keywords_analysis import fetch_keyword_suggestions  # Import the new function

app = Flask(__name__)

app.secret_key = '1234'  # Use a random, secure key for production


# Home route to render the input form
@app.route('/')
def home():
    return render_template('home.html')

def compress_data(data):
    return base64.b64encode(zlib.compress(json.dumps(data).encode())).decode()

def decompress_data(data):
    return json.loads(zlib.decompress(base64.b64decode(data)).decode())


@app.route('/metadata')
def metadata():
    return render_template('metadata.html')


@app.route("/get_metadata", methods=["GET", "POST"])
def metadata_analysis():
    # Initialize variables
    metadata_main = {}
    keyword_data_main = {}

    if request.method == "POST":
        # Extract user input from the form
        main_url = request.form.get("website")
        keyword = request.form.get("keyword")

        # Fetch metadata if provided
        if main_url:
            metadata_main = fetch_metadata(main_url)

        # Perform keyword analysis if a keyword is provided
        if keyword and main_url:
            keyword_data_main, body_text = analyze_keywords(main_url, keyword)

    data = {"Metadata":metadata_main, "Focus keyword entered by client":keyword ,"Keyword Density extracted from body text":keyword_data_main }
    recommendations = metadata_recommendations(data)

    # Render template with initialized variables to avoid UnboundLocalError
    return render_template(
        "metadata_analysis.html",
        metadata_main=metadata_main,
        keyword_data_main=keyword_data_main,
        recommendations = recommendations
    )


@app.route('/backlinks')
def backlinks():
    return render_template('backlinks.html')

@app.route('/backlink_recommendations')
def backlink_recommendations():
    data = decompress_data(session.pop('backlinks_data', None))  # Retrieve the backlinks data from session

    if not data:
        return "Error: No backlinks data found."

    recommendations = generate_seo_recommendations(data)
    insights = generate_seo_insights(data)

    return render_template('backlinks_r.html', recommendations=recommendations, insights=insights)


# Route to handle the API call and display results
@app.route('/get_backlinks', methods=['POST'])
def get_backlinks():
    input_web = request.form['website']  # Get the website from the form

    # Fetch backlinks data
    data = fetch_backlinks(input_web)

    if "error" in data:  # Check for errors in the response
        return render_template('results.html', error=data["error"])

    data1 = str(data)
    if len(data1) > 4200:
        data2 = {'url':data['url'],'domainRating':data['domainRating'],
        'urlRating':data['urlRating'], 'backlinks':data['backlinks'], 'refdomains':data['refdomains'],
        'dofollowBacklinks':data['dofollowBacklinks'], 'dofollowRefdomains':data['dofollowRefdomains'],
        'backlinksList':data['backlinksList'][:11] }
        session['backlinks_data'] = compress_data(data2)

    else:

        session['backlinks_data'] = compress_data(data)
    
    return render_template('results.html', data=data)

@app.route("/traffic_analysis", methods=["GET", "POST"])
def traffic_input():
    return render_template("traffic_input.html")

@app.route("/results", methods=["GET"])
def traffic_results():
    # Get user input
    website = request.args.get("website")

    # Get traffic history using the imported function
    traffic_history, data = get_traffic_history(website)

    if traffic_history is None:
        return render_template("traffic_results.html", error="API Error: Unable to fetch data")

    session['traffic_data'] = compress_data(data)

    return render_template("traffic_results.html", data=data, website=website, traffic_history=json.dumps(traffic_history))


@app.route('/traffic_recommendations')
def traffic_recommendations():
    data = decompress_data(session.pop('traffic_data', None))  # Retrieve the backlinks data from session
    session['traffic_data'] = compress_data(data)
    if not data:
        return "Error: No backlinks data found."

    recommendations = traffic_insights(data)

    return render_template('traffic_r.html', recommendations=recommendations)

@app.route('/keyword_input', methods=["GET"])
def keyword_input():
    return render_template("keyword_input.html")

@app.route('/keyword_analysis', methods=["POST"])
def keyword_analysis():
    keyword = request.form.get("keyword")
    search_engine = request.form.get("search_engine", "google")
    country = request.form.get("country", "us")

    if not keyword:
        return render_template("keyword_result.html", error="Keyword is required.")

    # Fetch keyword suggestions
    results = fetch_keyword_suggestions(keyword, search_engine, country)

    if "error" in results:
        return render_template("keyword_result.html", error=results["error"])

    return render_template("keyword_result.html", results=results)



@app.route('/compitator' , methods=["GET"])
def compitator():
    return render_template("compitator.html")

@app.route('/find_compitator', methods=["GET", "POST"])
def find_compitator():
    competitors = None
    error = None

    if request.method == "POST":
        keyword = request.form.get("keyword")
        country = request.form.get("country")
        num_results = request.form.get("num_results", type=int, default=10)

        num_results = min(num_results, 100)  # Ensure it's not more than 100

        if not keyword:
            error = "Keyword is required."
        else:
            result = find_compitators(keyword, country=country, num_results=num_results)

            if isinstance(result, dict) and "error" in result:
                error = result["error"]
            else:
                competitors = result

    # Get all country names for the dropdown
    countries = sorted([country.name for country in pycountry.countries])

    return render_template("find_compitator.html", countries=countries, competitors=competitors, error=error)

def compress_data(data):
    return base64.b64encode(zlib.compress(json.dumps(data).encode())).decode()

def decompress_data(data):
    return json.loads(zlib.decompress(base64.b64decode(data)).decode())

if __name__ == '__main__':
    app.run(debug=True)