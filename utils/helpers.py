def match_financial_data(financials, balance_sheets, profile):
    year_wise_data = []
    for fin in financials:
        year = fin.get('calendarYear') or (fin.get('date', '')[:4])
        bal = next((b for b in balance_sheets if (b.get('calendarYear') == year or (b.get('date', '')[:4] == year))), {})

        year_wise_data.append({
            'year': year,
            'employees': profile.get('fullTimeEmployees'),
            'revenue_usd': fin.get('revenue'),
            'profit_usd': fin.get('netIncome'),
            'share_capital_usd': bal.get('commonStock') or bal.get('shareCapital'),
            'market_cap_usd': profile.get('mktCap')
        })

    year_wise_data.sort(key=lambda x: int(x['year']) if x['year'] and x['year'].isdigit() else 0, reverse=True)
    return year_wise_data
