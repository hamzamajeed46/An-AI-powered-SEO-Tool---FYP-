from flask import Flask, render_template, request
from flask import session
from backlinks import fetch_backlinks, generate_seo_recommendations, generate_seo_insights
#from metadata_analysis import fetch_metadata, generate_recommendations, analyze_keywords

app = Flask(__name__)

app.secret_key = '1234'  # Use a random, secure key for production


# Home route to render the input form
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/backlinks')
def backlinks():
    return render_template('backlinks.html')

@app.route('/backlink_recommendations')
def backlink_recommendations():
    data = session.get('backlinks_data')  # Retrieve the backlinks data from session

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

    session['backlinks_data'] = data
    
    return render_template('results.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
