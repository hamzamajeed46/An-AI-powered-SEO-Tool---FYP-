from .app_routes import *
from .routes import *  

def register_routes(app):
    app.add_url_rule('/', view_func=home)
    app.add_url_rule('/login', view_func=login, methods=["GET", "POST"])
    app.add_url_rule('/signup', view_func=signup, methods=["GET", "POST"])
    app.add_url_rule('/logout', view_func=logout)

    app.add_url_rule('/metadata', view_func=metadata)
    app.add_url_rule('/get_metadata', view_func=metadata_analysis, methods=["GET", "POST"])

    app.add_url_rule('/compare_metadata', view_func=compare_metadata)
    app.add_url_rule('/get_compare_metadata', view_func=get_compare_metadata, methods=["POST"])

    app.add_url_rule('/backlinks', view_func=backlinks)
    app.add_url_rule('/get_backlinks', view_func=get_backlinks, methods=["POST"])
    app.add_url_rule('/backlink_recommendations', view_func=backlink_recommendations)

    app.add_url_rule('/compare_backlinks', view_func=compare_backlinks_route, methods=["GET", "POST"])

    app.add_url_rule('/traffic_analysis', view_func=traffic_input, methods=["GET", "POST"])
    app.add_url_rule('/results', view_func=traffic_results)
    app.add_url_rule('/traffic_recommendations', view_func=traffic_recommendations)

    app.add_url_rule('/keyword_input', view_func=keyword_input, methods=["GET"])
    app.add_url_rule('/keyword_analysis', view_func=keyword_analysis, methods=["POST"])

    app.add_url_rule('/competitor', view_func=compitator, methods=["GET"])
    app.add_url_rule('/find_competitor', view_func=find_compitator, methods=["GET", "POST"])

    app.add_url_rule('/compare_traffic', view_func=compare_traffic, methods=["GET", "POST"])

    app.add_url_rule('/report', view_func=report)
    app.add_url_rule('/download-report', view_func=download_report, methods=["GET"])
