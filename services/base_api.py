from abc import ABC, abstractmethod

class BaseCompanyAPI(ABC):

    @abstractmethod
    def search_company(self, company_name):
        pass

    @abstractmethod
    def get_company_data(self, symbol):
        pass
