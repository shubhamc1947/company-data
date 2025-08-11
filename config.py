import os
from dotenv import load_dotenv

load_dotenv()  # load .env variables

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    API_BASE_URL_US = os.getenv("API_BASE_URL_US", "<fall-back-us-url>")
    API_KEY_US = os.getenv("API_KEY_US", "<fall-back--us-key>")

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'app.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cache timeout in seconds (e.g., 24 hours)
    CACHE_TIMEOUT = 86400
    # Cache timeout for search results in seconds (e.g., 1 hour)
    SEARCH_CACHE_TIMEOUT = 3600
