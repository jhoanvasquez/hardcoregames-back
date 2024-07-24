import requests

from ecommerceHardcoregamesBack import settings


class AdapterEpaycoApi:
    base_url = settings.URL_EPAYCO_CONFIRM_SALE

    def __init__(self):
        pass

    def request_get(self, transaction_id):
        response = requests.get(self.base_url + transaction_id)
        return response.json()