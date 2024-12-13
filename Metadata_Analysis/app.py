from flask import Flask, render_template, request
from metadata_analysis import fetch_metadata, generate_recommendations, analyze_keywords


app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    # Render the home page with only a description
    return render_template("index.html")


@app.route("/metadata-analysis", methods=["GET", "POST"])
def metadata_analysis():
    # Initialize variables
    metadata_main = {}
    metadata_competitor = {}
    recommendations = ""
    keyword_data_main = {}
    keyword_data_competitor = {}

    if request.method == "POST":
        # Extract user input from the form
        main_url = request.form.get("main_url")
        competitor_url = request.form.get("competitor_url")
        keyword = request.form.get("keyword")

        # Fetch metadata if provided
        if main_url:
            metadata_main = fetch_metadata(main_url)
        if competitor_url:
            metadata_competitor = fetch_metadata(competitor_url)

        # Perform keyword analysis if a keyword is provided
        if keyword:
            if main_url:
                keyword_data_main = analyze_keywords(main_url, keyword)
            if competitor_url:
                keyword_data_competitor = analyze_keywords(competitor_url, keyword)

        # Generate recommendations based on keyword analysis and metadata
        recommendations = generate_recommendations(
            metadata_main,
            metadata_competitor
        )

    # Render template with initialized variables to avoid UnboundLocalError
    return render_template(
        "metadata_analysis.html",
        metadata_main=metadata_main,
        metadata_competitor=metadata_competitor,
        keyword_data_main=keyword_data_main,
        keyword_data_competitor=keyword_data_competitor,
        recommendations=recommendations,
    )


if __name__ == "__main__":
    app.run(debug=True)
