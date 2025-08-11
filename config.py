import os
from dotenv import load_dotenv

load_dotenv()  # load .env variables

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    API_BASE_URL_US = os.getenv("API_BASE_URL_US", "https://financialmodelingprep.com/api/v3")
    API_KEY_US = os.getenv("API_KEY_US", "5nR14kK8fixktAEey5CLd7s4pvE1mWRN")

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'app.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cache timeout in seconds (e.g., 24 hours)
    CACHE_TIMEOUT = 86400