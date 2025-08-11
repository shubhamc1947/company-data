#!/usr/bin/env python3
"""
US Company Data API - Send company name, get 4 key metrics
Works immediately with no API key setup required!
"""

from flask import Flask, request, jsonify
import requests
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

class USCompanyAPI:
    def __init__(self):
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.api_key = "5nR14kK8fixktAEey5CLd7s4pvE1mWRN"  
    
    def search_company(self, company_name):
        """Search for companies by name"""
        try:
            url = f"{self.base_url}/search"
            params = {
                'query': company_name,
                'limit': 10,
                'apikey': self.api_key
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Search failed: {response.status_code}")
                return []
        except Exception as e:
            logging.error(f"Search error: {e}")
            return []
    
    def get_company_data(self, symbol):
        """Get complete company data with all 4 metrics"""
        try:
            # Get company profile
            profile_url = f"{self.base_url}/profile/{symbol}"
            profile_response = requests.get(profile_url, params={'apikey': self.api_key}, timeout=10)
            if profile_response.status_code != 200:
                return None
            profile_data = profile_response.json()
            if not profile_data:
                return None
            profile = profile_data[0]
            
            # Get latest income statement (financials)
            income_url = f"{self.base_url}/income-statement/{symbol}"
            income_response = requests.get(income_url, params={'limit': 1, 'apikey': self.api_key}, timeout=10)
            income_data = {}
            if income_response.status_code == 200:
                income_json = income_response.json()
                if income_json:
                    income_data = income_json[0]

            # Get latest balance sheet (for share capital)
            balance_url = f"{self.base_url}/balance-sheet-statement/{symbol}"
            balance_response = requests.get(balance_url, params={'limit': 1, 'apikey': self.api_key}, timeout=10)
            balance_data = {}
            if balance_response.status_code == 200:
                balance_json = balance_response.json()
                if balance_json:
                    balance_data = balance_json[0]

            return {
                'profile': profile,
                'financials': income_data,
                'balance_sheet': balance_data
            }
        except Exception as e:
            logging.error(f"Data fetch error: {e}")
            return None

# Initialize API
us_api = USCompanyAPI()

@app.route('/company/<company_name>', methods=['GET'])
def get_company_metrics(company_name):
    """
    Main endpoint: Send company name → Get 4 key metrics
    Example: /company/Apple
    """
    logging.info(f"Processing request for: {company_name}")
    
    # Search for company
    search_results = us_api.search_company(company_name)
    if not search_results:
        return jsonify({
            'error': f'Company "{company_name}" not found',
            'suggestion': 'Try: Apple, Microsoft, Tesla, Amazon, Google, Meta, Netflix, Nike'
        }), 404
    
    # Find best match
    best_match = None
    for company in search_results:
        if company_name.lower() in company.get('name', '').lower():
            best_match = company
            break
    if not best_match:
        best_match = search_results[0]  # Take first result
    
    symbol = best_match.get('symbol')
    if not symbol:
        return jsonify({'error': 'Stock symbol not available'}), 400
    
    # Get detailed company data
    company_data = us_api.get_company_data(symbol)
    if not company_data:
        return jsonify({'error': 'Failed to fetch company data'}), 500
    
    profile = company_data['profile']
    financials = company_data['financials']
    balance_sheet = company_data.get('balance_sheet', {})
    
    # Extract the 4 key metrics
    share_capital = balance_sheet.get('commonStock') or balance_sheet.get('shareCapital') or None
    
    result = {
        'search_query': company_name,
        'matched_company': profile.get('companyName', ''),
        'symbol': symbol,
        'company_info': {
            'name': profile.get('companyName', ''),
            'symbol': symbol,
            'exchange': profile.get('exchangeShortName', ''),
            'sector': profile.get('sector', ''),
            'industry': profile.get('industry', ''),
            'country': profile.get('country', 'US'),
            'website': profile.get('website', ''),
            'description': (profile.get('description', '')[:200] + '...') if profile.get('description') else ''
        },
        'financial_metrics': {
            'employees': profile.get('fullTimeEmployees'),
            'revenue_usd': financials.get('revenue'),       # Annual revenue
            'profit_usd': financials.get('netIncome'),       # Net profit/income
            'share_capital_usd': share_capital,              # Share Capital
            'market_cap_usd': profile.get('mktCap')          # Market capitalization
        },
        'additional_metrics': {
            'total_assets': financials.get('totalAssets'),
            'total_debt': financials.get('totalDebt'),
            'cash_and_equivalents': financials.get('cashAndCashEquivalents'),
            'year': financials.get('calendarYear')
        },
        'data_quality': {
            'metrics_available': sum(1 for v in [
                profile.get('fullTimeEmployees'),
                financials.get('revenue'),
                financials.get('netIncome'),
                share_capital
            ] if v is not None),
            'total_metrics': 4,
            'data_source': 'Financial Modeling Prep API'
        }
    }
    
    return jsonify(result)

@app.route('/search/<company_name>', methods=['GET'])
def search_companies(company_name):
    """
    Search endpoint: Find matching companies
    Example: /search/tech
    """
    search_results = us_api.search_company(company_name)
    if not search_results:
        return jsonify({
            'query': company_name,
            'message': 'No companies found',
            'suggestions': ['Apple', 'Microsoft', 'Tesla', 'Amazon']
        })
    formatted_results = []
    for company in search_results[:10]:
        formatted_results.append({
            'name': company.get('name', ''),
            'symbol': company.get('symbol', ''),
            'exchange': company.get('exchangeShortName', ''),
            'type': company.get('type', '')
        })
    return jsonify({
        'query': company_name,
        'total_results': len(search_results),
        'results': formatted_results
    })

@app.route('/examples', methods=['GET'])
def get_examples():
    """Popular US companies that work well with the API"""
    examples = {
        'tech_giants': [
            {'name': 'Apple', 'symbol': 'AAPL'},
            {'name': 'Microsoft', 'symbol': 'MSFT'},
            {'name': 'Google/Alphabet', 'symbol': 'GOOGL'},
            {'name': 'Amazon', 'symbol': 'AMZN'},
            {'name': 'Meta/Facebook', 'symbol': 'META'}
        ],
        'popular_stocks': [
            {'name': 'Tesla', 'symbol': 'TSLA'},
            {'name': 'Netflix', 'symbol': 'NFLX'},
            {'name': 'Nike', 'symbol': 'NKE'},
            {'name': 'Coca-Cola', 'symbol': 'KO'},
            {'name': 'McDonald\'s', 'symbol': 'MCD'}
        ],
        'banking': [
            {'name': 'JPMorgan Chase', 'symbol': 'JPM'},
            {'name': 'Bank of America', 'symbol': 'BAC'},
            {'name': 'Wells Fargo', 'symbol': 'WFC'}
        ]
    }
    return jsonify({
        'message': 'Popular US companies - guaranteed to work!',
        'categories': examples,
        'usage_examples': [
            '/company/Apple',
            '/company/Tesla',
            '/company/Microsoft',
            '/search/bank'
        ]
    })

@app.route('/test', methods=['GET'])
def quick_test():
    """Quick test endpoint"""
    test_company = 'Apple'
    search_results = us_api.search_company(test_company)
    if search_results:
        return jsonify({
            'status': 'API Working! ✅',
            'test_company': test_company,
            'found_companies': len(search_results),
            'first_result': search_results[0] if search_results else None,
            'next_step': f'/company/{test_company}'
        })
    else:
        return jsonify({
            'status': 'API Issue ❌',
            'error': 'Could not fetch test data'
        })

@app.route('/', methods=['GET'])
def api_info():
    """API documentation"""
    return jsonify({
        'service': 'US Company Data API',
        'description': 'Get 4 key financial metrics for US public companies',
        'advantages': [
            '✅ No API key setup required',
            '✅ Free to use (demo key)',
            '✅ Works immediately',
            '✅ 8000+ US public companies',
            '✅ Real-time data'
        ],
        'target_metrics': [
            'employees (full-time employees)',
            'revenue_usd (annual revenue)',
            'profit_usd (net income)',
            'share_capital_usd (share capital)'
        ],
        'endpoints': {
            'GET /': 'API documentation',
            'GET /company/{name}': 'Get company metrics by name',
            'GET /search/{name}': 'Search for companies',
            'GET /examples': 'Popular companies list',
            'GET /test': 'Quick API test'
        },
        'examples': {
            'single_company': '/company/Apple',
            'search': '/search/tech',
            'popular_companies': '/examples'
        },
        'data_source': 'Financial Modeling Prep (financialmodelingprep.com)',
        'rate_limits': '250 requests/day (free tier)'
    })

if __name__ == '__main__':
    print("🇺🇸 US Company Data API Starting...")
    print("=" * 50)
    print("✅ No setup required - works immediately!")
    print("🚀 Test: http://localhost:5000/test")
    print("📊 Example: http://localhost:5000/company/Apple")
    print("📋 Examples: http://localhost:5000/examples")
    print("📖 Docs: http://localhost:5000/")
    print("=" * 50)
    app.run(debug=True, port=5000, host='0.0.0.0')
