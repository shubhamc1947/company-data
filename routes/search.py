from flask import Blueprint, jsonify, current_app
from services.factory import APIServiceFactory

bp = Blueprint('search', __name__, url_prefix='/search')

@bp.route('/<country>/<company_name>', methods=['GET'])
def search_companies(country, company_name):
    current_app.logger.info(f"Search request for '{company_name}' in country '{country}'")
    try:
        api_service = APIServiceFactory.get_service(country)
    except ValueError as e:
        current_app.logger.error(str(e))
        return jsonify({'error': str(e)}), 404

    search_results = api_service.search_company(company_name)
    if not search_results:
        return jsonify({
            'query': company_name,
            'message': f'No companies found in {country.upper()}',
            'suggestions': ['Apple', 'Microsoft', 'Tesla', 'Amazon']
        })
    formatted_results = [{
        'name': c.get('name', ''),
        'symbol': c.get('symbol', ''),
        'exchange': c.get('exchangeShortName', ''),
        'type': c.get('type', '')
    } for c in search_results[:10]]
    return jsonify({
        'query': company_name,
        'total_results': len(search_results),
        'results': formatted_results
    })
