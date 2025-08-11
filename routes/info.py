from flask import Blueprint, jsonify, current_app
from services.us_api import USCompanyAPI

bp = Blueprint('info', __name__)
us_api = USCompanyAPI()

@bp.route('/', methods=['GET'])
def api_info():
    current_app.logger.info("API info requested")
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
        }
    })

@bp.route('/examples', methods=['GET'])
def get_examples():
    current_app.logger.info("Examples endpoint requested")
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
            {'name': "McDonald's", 'symbol': 'MCD'}
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

@bp.route('/test', methods=['GET'])
def quick_test():
    test_company = 'Apple'
    current_app.logger.info(f"Running quick test with company: {test_company}")
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
