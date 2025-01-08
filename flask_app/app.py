from flask import Flask, render_template, request
from backlinks import fetch_backlinks, generate_seo_recommendations

app = Flask(__name__)

# Home route to render the input form
@app.route('/')
def home():
    return render_template('backlinks.html')

# Route to handle the API call and display results
@app.route('/get_backlinks', methods=['POST'])
def get_backlinks():
    input_web = request.form['website']  # Get the website from the form

    # Fetch backlinks data
    data = fetch_backlinks(input_web)

    if "error" in data:  # Check for errors in the response
        return render_template('results.html', error=data["error"])

    # Generate SEO recommendations
    recommendations = generate_seo_recommendations(data)
    return render_template('results.html', data=data, recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
