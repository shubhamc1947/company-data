import requests
import logging
import time
from config import Config
from services.base_api import BaseCompanyAPI
from models import db, Company, CompanyProfile, FinancialStatement
from utils.helpers import match_financial_data # We will use the helper now

logger = logging.getLogger(__name__)

class USCompanyAPI(BaseCompanyAPI):
    def __init__(self):
        self.base_url = Config.API_BASE_URL_US
        self.api_key = Config.API_KEY_US
        self.country_code = 'us'

    def search_company(self, company_name):
        # This function does not need caching as search results should be live
        logger.info(f"[US] Searching company '{company_name}'")
        url = f"{self.base_url}/search"
        params = {'query': company_name, 'limit': 10, 'apikey': self.api_key}
        try:
            response = requests.get(url, params=params, timeout=10)
            logger.info(f"[US] Search API status: {response.status_code}")
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            logger.error(f"[US] Error during search: {e}")
            return []

    def get_company_data(self, symbol):
        logger.info(f"[US] Requesting data for symbol: {symbol}")
        
        # 1. Check the cache first
        company = Company.query.filter_by(symbol=symbol, country_code=self.country_code).first()

        if company and company.profile and not company.profile.is_stale(Config.CACHE_TIMEOUT):
            logger.info(f"[US] Cache HIT for symbol: {symbol}")
            return self._format_data_from_db(company)

        logger.info(f"[US] Cache MISS or STALE for symbol: {symbol}. Fetching from API.")
        
        # 2. If not in cache or stale, fetch from API
        api_data = self._fetch_from_api(symbol)
        if not api_data:
            return None
        
        # 3. Save to database
        self._save_to_db(symbol, api_data)

        # 4. Return formatted data
        # Re-fetch from DB to ensure consistency
        company = Company.query.filter_by(symbol=symbol, country_code=self.country_code).first()
        return self._format_data_from_db(company)

    def _fetch_from_api(self, symbol):
        """Internal method to fetch all required data from the external API."""
        try:
            profile_url = f"{self.base_url}/profile/{symbol}"
            profile_res = requests.get(profile_url, params={'apikey': self.api_key}, timeout=10)
            if profile_res.status_code != 200 or not profile_res.json():
                logger.error(f"[US] Profile API failed for {symbol}")
                return None
            profile = profile_res.json()[0]

            income_url = f"{self.base_url}/income-statement/{symbol}"
            income_res = requests.get(income_url, params={'limit': 5, 'apikey': self.api_key}, timeout=10)
            income_data = income_res.json() if income_res.status_code == 200 else []

            balance_url = f"{self.base_url}/balance-sheet-statement/{symbol}"
            balance_res = requests.get(balance_url, params={'limit': 5, 'apikey': self.api_key}, timeout=10)
            balance_data = balance_res.json() if balance_res.status_code == 200 else []

            return {'profile': profile, 'financials': income_data, 'balance_sheet': balance_data}
        except Exception as e:
            logger.error(f"[US] Error fetching company data from API: {e}")
            return None

    def _save_to_db(self, symbol, data):
        """Saves the fetched API data into the database."""
        profile_data = data['profile']
        
        # Use the helper to merge financial data
        year_wise_data = match_financial_data(data['financials'], data['balance_sheet'], profile_data)

        # Find or create the main company entry
        company = Company.query.filter_by(symbol=symbol, country_code=self.country_code).first()
        if not company:
            company = Company(symbol=symbol, name=profile_data.get('companyName', ''), country_code=self.country_code)
            db.session.add(company)
        
        # Delete old profile if it exists
        if company.profile:
            db.session.delete(company.profile)

        # Create new profile
        new_profile = CompanyProfile(
            company=company,
            exchange=profile_data.get('exchangeShortName'),
            sector=profile_data.get('sector'),
            industry=profile_data.get('industry'),
            description=profile_data.get('description'),
            website=profile_data.get('website'),
            full_time_employees=profile_data.get('fullTimeEmployees'),
            market_cap_usd=profile_data.get('mktCap'),
            last_updated_ts=int(time.time())
        )
        db.session.add(new_profile)

        # Delete old financial statements
        company.financials.delete()

        # Add new financial statements
        for row in year_wise_data:
            if not row.get('year'): continue
            statement = FinancialStatement(
                company=company,
                year=row['year'],
                revenue_usd=row.get('revenue_usd'),
                profit_usd=row.get('profit_usd'),
                share_capital_usd=row.get('share_capital_usd')
            )
            db.session.add(statement)
        
        db.session.commit()
        logger.info(f"[US] Saved data for {symbol} to database.")

    def _format_data_from_db(self, company):
        """Formats data from DB objects into the dictionary structure the route expects."""
        if not company or not company.profile:
            return None
        
        profile_dict = {
            'companyName': company.name,
            'symbol': company.symbol,
            'exchangeShortName': company.profile.exchange,
            'sector': company.profile.sector,
            'industry': company.profile.industry,
            'country': company.country_code.upper(),
            'website': company.profile.website,
            'description': company.profile.description,
            'fullTimeEmployees': company.profile.full_time_employees,
            'mktCap': company.profile.market_cap_usd
        }

        financials_list = []
        # Sort financials by year descending
        sorted_financials = company.financials.order_by(FinancialStatement.year.desc()).all()
        for fin in sorted_financials:
            financials_list.append({
                'year': fin.year,
                'employees': company.profile.full_time_employees,
                'revenue_usd': fin.revenue_usd,
                'profit_usd': fin.profit_usd,
                'share_capital_usd': fin.share_capital_usd,
                'market_cap_usd': company.profile.market_cap_usd
            })

        return {
            'profile': profile_dict,
            'year_wise_financials': financials_list
        }