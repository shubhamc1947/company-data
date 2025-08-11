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

    search_results = api_service.search_company(company_name)
    if not search_results:
        return jsonify({
            'error': f'Company "{company_name}" not found in {country.upper()}',
            'suggestion': 'Try: Apple, Microsoft, Tesla, Amazon, Google, Meta, Netflix, Nike'
        }), 404

    best_match = next((c for c in search_results if company_name.lower() in c.get('name', '').lower()), search_results[0])
    symbol = best_match.get('symbol')
    if not symbol:
        return jsonify({'error': 'Stock symbol not available'}), 400

    company_data = api_service.get_company_data(symbol)
    if not company_data:
        return jsonify({'error': 'Failed to fetch company data'}), 500

    profile = company_data['profile']
    financials = company_data['financials']
    balance_sheets = company_data['balance_sheet']

    year_wise_data = []
    for fin in financials:
        year = fin.get('calendarYear') or fin.get('date', '')[:4]
        bal = next((b for b in balance_sheets if b.get('calendarYear') == year or b.get('date', '')[:4] == year), {})

        year_wise_data.append({
            'year': year,
            'employees': profile.get('fullTimeEmployees'),
            'revenue_usd': fin.get('revenue'),
            'profit_usd': fin.get('netIncome'),
            'share_capital_usd': bal.get('commonStock') or bal.get('shareCapital'),
            'market_cap_usd': profile.get('mktCap')
        })

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
            'country': profile.get('country', country.upper()),
            'website': profile.get('website', ''),
            'description': (profile.get('description', '')[:200] + '...') if profile.get('description') else ''
        },
        'year_wise_financials': year_wise_data,
        'data_quality': {
            'data_source': f'{country.upper()} API'
        }
    }
    return jsonify(result)
