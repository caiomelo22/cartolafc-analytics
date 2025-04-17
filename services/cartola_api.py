import requests

class CartolaFCAPI:
    def __init__(self):
        self.base_url = "https://api.cartola.globo.com"

    def get_matches(self):
        url = f"{self.base_url}/partidas"
        response = requests.get(url)
        return response.json()
