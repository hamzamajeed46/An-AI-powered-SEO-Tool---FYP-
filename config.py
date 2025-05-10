from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    API_KEY1 = os.getenv('API_KEY1')
    LLM_API = os.getenv('LLM_API')
