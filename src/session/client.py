from curl_cffi import requests as cffi

from src.config import Config

class Client:
    def __init__(self, config: Config, proxy: str | None = None):
        self.config = config
        self.proxy = proxy
        self.session = cffi.Session(impersonate=config.impersonate)
        self.session.headers.update(
            {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-GB,en;q=0.9",
                "Referer": config.referer,
            }
        )
        self.cookies = {}

    def mapping(self) -> dict:
        if not self.proxy:
            return {}
        proxy = self.proxy
        if "://" not in proxy:
            proxy = f"http://{proxy}"
        return {"http": proxy, "https": proxy}

    def get(self, url: str) -> cffi.Response:
        response = self.session.get(
            url,
            proxies=self.mapping(),
            timeout=self.config.timeout,
            verify=False,
        )
        response.raise_for_status()
        return response

    def post(self, url: str, body: str, headers: dict | None = None) -> cffi.Response:
        merged = {"Content-Type": "text/plain;charset=UTF-8"}
        if headers:
            merged.update(headers)
        response = self.session.post(
            url,
            data=body.encode("utf-8"),
            headers=merged,
            proxies=self.mapping(),
            timeout=self.config.timeout,
            verify=False,
        )
        response.raise_for_status()
        return response
