from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_USERNAME = os.getenv('DB_USERNAME')
    API_KEY = os.getenv('API_KEY')
    LLM_API = os.getenv('LLM_API')
