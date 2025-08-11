from services.us_api import USCompanyAPI
# from services.uk_api import UKCompanyAPI
# from services.italy_api import ItalyCompanyAPI

class APIServiceFactory:
    _services = {
        'us': USCompanyAPI(),
        # 'uk': UKCompanyAPI(),
        # 'it': ItalyCompanyAPI(),
    }

    @classmethod
    def get_service(cls, country_code: str):
        service = cls._services.get(country_code.lower())
        if not service:
            raise ValueError(f"No service found for country code: {country_code}")
        return service
