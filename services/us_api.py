import requests
import logging
from config import Config
from services.base_api import BaseCompanyAPI

logger = logging.getLogger(__name__)

class USCompanyAPI(BaseCompanyAPI):
    def __init__(self):
        self.base_url = Config.API_BASE_URL_US
        self.api_key = Config.API_KEY_US

    def search_company(self, company_name):
        logger.info(f"[US] Searching company '{company_name}'")
        url = f"{self.base_url}/search"
        params = {'query': company_name, 'limit': 10, 'apikey': self.api_key}
        try:
            response = requests.get(url, params=params, timeout=10)
            logger.info(f"[US] Search API status: {response.status_code}")
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"[US] Search failed with status: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"[US] Error during search: {e}")
            return []

    def get_company_data(self, symbol):
        logger.info(f"[US] Fetching data for symbol: {symbol}")
        try:
            profile_url = f"{self.base_url}/profile/{symbol}"
            profile_response = requests.get(profile_url, params={'apikey': self.api_key}, timeout=10)
            if profile_response.status_code != 200:
                logger.error(f"[US] Profile API failed with status {profile_response.status_code}")
                return None
            profile_data = profile_response.json()
            if not profile_data:
                logger.warning("[US] No profile data found")
                return None
            profile = profile_data[0]

            income_url = f"{self.base_url}/income-statement/{symbol}"
            income_response = requests.get(income_url, params={'limit': 5, 'apikey': self.api_key}, timeout=10)
            income_data = income_response.json() if income_response.status_code == 200 else []

            balance_url = f"{self.base_url}/balance-sheet-statement/{symbol}"
            balance_response = requests.get(balance_url, params={'limit': 5, 'apikey': self.api_key}, timeout=10)
            balance_data = balance_response.json() if balance_response.status_code == 200 else []

            return {'profile': profile, 'financials': income_data, 'balance_sheet': balance_data}
        except Exception as e:
            logger.error(f"[US] Error fetching company data: {e}")
            return None
