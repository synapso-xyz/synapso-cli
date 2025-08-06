import requests


class SynapsoRestClientError(Exception):
    pass


def _handle_response(response: requests.Response):
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise SynapsoRestClientError(f"HTTP error: {e}") from e
    except requests.exceptions.RequestException as e:
        raise SynapsoRestClientError(f"Request error: {e}") from e
    return response.json()


class SynapsoRestClient:
    def __init__(self, base_url: str):
        if not base_url.startswith(("http://", "https://", "localhost")):
            raise ValueError(
                "base_url must start with 'http://', 'https://', or 'localhost'"
            )
        self.base_url = base_url

    def get_cortex_list(self):
        response = requests.get(f"{self.base_url}/cortex/list", timeout=300)
        return _handle_response(response)

    def get_cortex(self, cortex_id: str | None = None, cortex_name: str | None = None):
        url = f"{self.base_url}/cortex"
        params = {}
        if cortex_id:
            params["cortex_id"] = cortex_id
        if cortex_name:
            params["cortex_name"] = cortex_name
        response = requests.get(url, params=params, timeout=300)
        return _handle_response(response)

    def create_cortex(self, path: str, cortex_name: str):
        url = f"{self.base_url}/cortex/create"
        data = {
            "path": path,
            "name": cortex_name,
        }
        response = requests.post(url, json=data, timeout=300)
        return _handle_response(response)

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
        return _handle_response(response)

    def query(self, query: str):
        url = f"{self.base_url}/query/query"
        data = {
            "query": query,
        }
        response = requests.post(url, json=data, timeout=300)
        return _handle_response(response)

    def system_init(self):
        url = f"{self.base_url}/system/init"
        response = requests.post(url, timeout=300)
        return _handle_response(response)
