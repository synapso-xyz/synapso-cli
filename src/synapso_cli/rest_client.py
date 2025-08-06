import requests


class SynapsoRestClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_cortex_list(self):
        response = requests.get(f"{self.base_url}/cortex/list", timeout=300)
        return response.json()

    def get_cortex(self, cortex_id: str | None = None, cortex_name: str | None = None):
        url = f"{self.base_url}/cortex"
        params = {}
        if cortex_id:
            params["cortex_id"] = cortex_id
        if cortex_name:
            params["cortex_name"] = cortex_name
        response = requests.get(url, params=params, timeout=300)
        return response.json()

    def create_cortex(self, path: str, cortex_name: str):
        url = f"{self.base_url}/cortex/create"
        data = {
            "path": path,
            "name": cortex_name,
        }
        response = requests.post(url, json=data, timeout=300)
        return response.json()

    def index_cortex(
        self, cortex_id: str | None = None, cortex_name: str | None = None
    ):
        url = f"{self.base_url}/cortex/index"
        params = {}
        if cortex_id:
            params["cortex_id"] = cortex_id
        if cortex_name:
            params["cortex_name"] = cortex_name
        response = requests.post(url, params=params, timeout=300)
        return response.json()

    def query(self, query: str):
        url = f"{self.base_url}/query/query"
        data = {
            "query": query,
        }
        response = requests.post(url, json=data, timeout=300)
        return response.json()

    def system_init(self):
        url = f"{self.base_url}/system/init"
        response = requests.post(url, timeout=300)
        return response.json()
