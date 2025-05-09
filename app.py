from flask import Flask, render_template, request, redirect, url_for
from flask import session, send_file
import zlib
import base64
import json
import pycountry
from pymongo import MongoClient
from compitator import find_compitators,compare_backlinks
from backlinks import fetch_backlinks, generate_seo_recommendations, generate_seo_insights
from metadata_analysis import fetch_metadata, metadata_recommendations
from traffic import get_traffic_history, traffic_insights
from keywords_analysis import fetch_keyword_suggestions, generate_blog_from_keyword, generate_image_from_keyword
from compare_traffic import fetch_traffic_data, generate_llm_comparison_insights
from signin import login_route, signup_route
from compare_metadata import compare_metadata2, generate_comparison_recommendations
from report import create_seo_report


app = Flask(__name__)

app.secret_key = '1234'  # Use a random, secure key for production


def get_db_connection():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['seotool']  # Replace with your DB name
        print("Connected to MongoDB successfully!")
        return db
    except Exception as e:
        print("MongoDB connection failed:", e)
        return None

@app.route('/')
def home():
    '''
    if 'user_id' in session:
        return render_template('home.html', username=session['username'])
    else:
        return redirect(url_for('login'))
    '''
    return render_template('home.html')
    
# Login route
@app.route('/login', methods=["GET", "POST"])
def login():
    return login_route()

# Sign-up route
@app.route('/signup', methods=["GET", "POST"])
def signup():
    return signup_route()

# Log out route to end session
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


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
        if keyword and main_url:
            metadata_main, keyword_data_main, body_text = fetch_metadata(main_url, keyword)

        # Perform keyword analysis if a keyword is provided
        if main_url:
            metadata_main = fetch_metadata(main_url)
    data = {"Metadata":metadata_main, "Focus keyword entered by client":keyword ,"Keyword Density extracted from body text":keyword_data_main }
    recommendations = metadata_recommendations(data)

    # Render template with initialized variables to avoid UnboundLocalError
    return render_template(
        "metadata_analysis.html",
        metadata_main=metadata_main,
        keyword_data_main=keyword_data_main,
        recommendations = recommendations
    )


@app.route('/compare_metadata')
def compare_metadata():
    return render_template('compare_metadata.html')

@app.route('/get_compare_metadata', methods=['POST'])
def get_compare_metadata():
    if request.method == 'POST':
        url1 = request.form.get('website1')
        url2 = request.form.get('website2')
        keyword = request.form.get('keyword')

        comparison_result = compare_metadata2(url1, url2, keyword)
        recommendations = generate_comparison_recommendations(comparison_result)

        return render_template(
            'compare_metadata_result.html',
            results=comparison_result,
            recommendations=recommendations
        )



@app.route('/backlinks')
def backlinks():
    return render_template('backlinks.html')

@app.route('/backlink_recommendations')
def backlink_recommendations():
    backlinks_data = session['backlinks_data']
    data = decompress_data(backlinks_data)  # Retrieve the backlinks data from session

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
    countries = sorted([country.name for country in pycountry.countries])
    return render_template("keyword_input.html", countries=countries)

@app.route('/keyword_analysis', methods=["POST"])
def keyword_analysis():
    keyword = request.form.get("keyword")
    search_engine = request.form.get("search_engine", "google")
    country = request.form.get("country", "us")

    if not keyword:
        return render_template("keyword_result.html", error="Keyword is required.")

    # Fetch keyword suggestions
    results = fetch_keyword_suggestions(keyword, search_engine, country)
    image = generate_image_from_keyword(keyword)

    if "error" in results:
        return render_template("keyword_result.html", error=results["error"])
    

    return render_template("keyword_result.html", results=results)
@app.route("/generate_blog", methods=["POST"])
def generate_blog():
    keyword = request.form.get("keyword")

    if not keyword:
        return render_template("keyword_result.html", error="Keyword is required.")

    prompt = f"Write a detailed SEO-optimized blog post about '{keyword}' with subheadings."

    try:
        blog_html = generate_blog_from_keyword(prompt, keyword)  # Use your LLM function here
        image_url,image_url1 = generate_image_from_keyword(keyword)
        return render_template("blog_result.html", blog_content=blog_html, image_url=image_url, image_url1=image_url1, keyword=keyword)
    except Exception as e:
        return render_template("keyword_result.html", error=f"Error: {str(e)}")



@app.route('/competitor' , methods=["GET"])
def compitator():
    return render_template("competitor.html")

@app.route('/find_competitor', methods=["GET", "POST"])
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

    return render_template("find_competitor.html", countries=countries, competitors=competitors, error=error)

def compress_data(data):
    return base64.b64encode(zlib.compress(json.dumps(data).encode())).decode()

def decompress_data(data):
    return json.loads(zlib.decompress(base64.b64decode(data)).decode())
@app.route('/compare_backlinks', methods=["GET", "POST"])
def compare_backlinks_route():
    error = None

    if request.method == "POST":
        main_website = request.form.get("main_website")
        competitor_website = request.form.get("competitor_website")

        if not main_website or not competitor_website:
            error = "Both website URLs are required."
            return render_template("c_backlinks_input.html", error=error)

        comparison_result = compare_backlinks(main_website, competitor_website)

        if "error" in comparison_result:
            error = comparison_result["error"]
            return render_template("c_backlinks_input.html", error=error)

        return render_template("c_backlinks_result.html", result=comparison_result)

    return render_template("c_backlinks_input.html")



@app.route("/compare_traffic", methods=["GET", "POST"])
def compare_traffic():
    if request.method == "POST":
        website1 = request.form.get("website1")
        website2 = request.form.get("website2")

        history1, data1 = fetch_traffic_data(website1)
        history2, data2 = fetch_traffic_data(website2)

        if not data1 or not data2:
            return render_template("compare_traffic.html", error="Failed to fetch data for one or both websites.")

        insights = generate_llm_comparison_insights(data1, data2, website1, website2)

        return render_template("compare_traffic_result.html",
                               website1=website1,
                               website2=website2,
                               data1=data1,
                               data2=data2,
                               history1=json.dumps(history1),
                               history2=json.dumps(history2),
                               insights=insights)

    return render_template("compare_traffic.html")


@app.route("/report")
def report():
    return render_template("report.html")


@app.route('/download-report', methods=['GET'])
def download_report():
    website = request.args.get("website")
    keyword = request.args.get("keyword")
    if not website:
        return "Website parameter is required", 400
    return create_seo_report(website)

if __name__ == '__main__':
    app.run(debug=True)
