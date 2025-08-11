from flask import Blueprint, jsonify, current_app
from services.factory import APIServiceFactory

bp = Blueprint('company', __name__, url_prefix='/company')

@bp.route('/<country>/<company_name>', methods=['GET'])
def get_company_metrics(country, company_name):
    current_app.logger.info(f"Request for company '{company_name}' in country '{country}'")

    try:
        api_service = APIServiceFactory.get_service(country)
    except ValueError as e:
        current_app.logger.error(str(e))
        return jsonify({'error': str(e)}), 404

    # Search for the company to get the correct symbol
    search_results = api_service.search_company(company_name)
    if not search_results:
        return jsonify({
            'error': f'Company "{company_name}" not found in {country.upper()}',
            'suggestion': 'Try: Apple, Microsoft, Tesla, Amazon, Google, Meta, Netflix, Nike'
        }), 404

    # --- REVISED LOGIC FOR CHOOSING BEST MATCH ---
    primary_exchanges = ['NASDAQ', 'NYSE']
    best_match = None

    # 1. Prioritize exact symbol match on primary US exchanges
    for c in search_results:
        if c.get('symbol', '').upper() == company_name.upper() and c.get('exchangeShortName', '') in primary_exchanges:
            best_match = c
            current_app.logger.info(f"Found best match by exact symbol on primary exchange: {best_match.get('symbol')}")
            break

    # 2. If not found, prioritize name match on primary exchanges
    if not best_match:
        for c in search_results:
            if company_name.lower() in c.get('name', '').lower() and c.get('exchangeShortName', '') in primary_exchanges:
                best_match = c
                current_app.logger.info(f"Found best match by name on primary exchange: {best_match.get('symbol')}")
                break

    # 3. As a fallback, take the first result from the API list (often the most relevant)
    if not best_match and search_results:
        best_match = search_results[0]
        current_app.logger.info(f"Using first search result as fallback: {best_match.get('symbol')}")


    if not best_match:
        return jsonify({'error': 'Could not determine a best match from search results.'}), 404

    symbol = best_match.get('symbol')
    if not symbol:
        return jsonify({'error': 'Stock symbol not available for the best match.'}), 400

    # The service layer now handles caching internally
    processed_data = api_service.get_company_data(symbol)
    if not processed_data:
        return jsonify({'error': f'Failed to fetch or process data for symbol {symbol}'}), 500

    # The data is already processed, we just need to format the final response
    profile = processed_data['profile']
    year_wise_data = processed_data['year_wise_financials']

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
            'country': profile.get('country', country.upper()),
            'website': profile.get('website', ''),
            'description': (profile.get('description', '')[:200] + '...') if profile.get('description') else ''
        },
        'year_wise_financials': year_wise_data,
        'data_quality': {
            'data_source': f'Cached {country.upper()} API Data'
        }
    }
    return jsonify(result)
