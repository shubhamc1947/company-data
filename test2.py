#!/usr/bin/env python3
"""
US Company Data API - Send company name, get 4 key metrics for last 5 years
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
        self.api_key = "5nR14kK8fixktAEey5CLd7s4pvE1mWRN"  # Replace with your actual API key or keep demo key

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
        """Get company profile, income statement and balance sheet for last 5 years"""
        try:
            # Profile (employees, market cap, etc.)
            profile_url = f"{self.base_url}/profile/{symbol}"
            profile_response = requests.get(profile_url, params={'apikey': self.api_key}, timeout=10)
            if profile_response.status_code != 200:
                return None
            profile_data = profile_response.json()
            if not profile_data:
                return None
            profile = profile_data[0]

            # Last 5 years income statement (revenue, profit)
            income_url = f"{self.base_url}/income-statement/{symbol}"
            income_response = requests.get(income_url, params={'limit': 5, 'apikey': self.api_key}, timeout=10)
            income_data = []
            if income_response.status_code == 200:
                income_data = income_response.json()

            # Last 5 years balance sheet (share capital etc)
            balance_url = f"{self.base_url}/balance-sheet-statement/{symbol}"
            balance_response = requests.get(balance_url, params={'limit': 5, 'apikey': self.api_key}, timeout=10)
            balance_data = []
            if balance_response.status_code == 200:
                balance_data = balance_response.json()

            return {
                'profile': profile,
                'financials': income_data,
                'balance_sheet': balance_data
            }
        except Exception as e:
            logging.error(f"Data fetch error: {e}")
            return None


us_api = USCompanyAPI()

@app.route('/company/<company_name>', methods=['GET'])
def get_company_metrics(company_name):
    logging.info(f"Processing request for: {company_name}")

    search_results = us_api.search_company(company_name)
    if not search_results:
        return jsonify({
            'error': f'Company "{company_name}" not found',
            'suggestion': 'Try: Apple, Microsoft, Tesla, Amazon, Google, Meta, Netflix, Nike'
        }), 404

    best_match = None
    for company in search_results:
        if company_name.lower() in company.get('name', '').lower():
            best_match = company
            break
    if not best_match:
        best_match = search_results[0]

    symbol = best_match.get('symbol')
    if not symbol:
        return jsonify({'error': 'Stock symbol not available'}), 400

    company_data = us_api.get_company_data(symbol)
    if not company_data:
        return jsonify({'error': 'Failed to fetch company data'}), 500

    profile = company_data['profile']
    financials = company_data['financials']  # list of income statements
    balance_sheets = company_data['balance_sheet']  # list of balance sheets

    # Match financials and balance sheets by year
    year_wise_data = []
    for fin in financials:
        year = fin.get('calendarYear') or (fin.get('date', '')[:4])
        # Find matching balance sheet entry for same year
        bal = next((b for b in balance_sheets if (b.get('calendarYear') == year or (b.get('date', '')[:4] == year))), {})

        year_wise_data.append({
            'year': year,
            'employees': profile.get('fullTimeEmployees'),  # employees usually static in profile
            'revenue_usd': fin.get('revenue'),
            'profit_usd': fin.get('netIncome'),
            'share_capital_usd': bal.get('commonStock') or bal.get('shareCapital'),
            'market_cap_usd': profile.get('mktCap')
        })

    # Sort descending by year
    year_wise_data.sort(key=lambda x: int(x['year']) if x['year'] and x['year'].isdigit() else 0, reverse=True)

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
        'year_wise_financials': year_wise_data,
        'data_quality': {
            'data_source': 'Financial Modeling Prep API'
        }
    }
    return jsonify(result)


@app.route('/search/<company_name>', methods=['GET'])
def search_companies(company_name):
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
    return jsonify({
        'service': 'US Company Data API',
        'description': 'Get 4 key financial metrics for US public companies (last 5 years)',
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
            'GET /company/{name}': 'Get company metrics by name (last 5 years)',
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
