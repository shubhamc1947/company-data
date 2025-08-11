import os
from dotenv import load_dotenv

load_dotenv()  # load .env variables

class Config:
    API_BASE_URL_US = os.getenv("API_BASE_URL_US", "https://financialmodelingprep.com/api/v3")
    API_KEY_US = os.getenv("API_KEY_US", "5nR14kK8fixktAEey5CLd7s4pvE1mWRN")
