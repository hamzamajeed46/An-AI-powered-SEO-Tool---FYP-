from flask import Flask
from .routes import register_routes

def create_app():
    app = Flask(__name__)
    app.secret_key = '1234'  # In production, read from environment variable or config file

    # Register routes from the app
    register_routes(app)

    return app
