import json
from pathlib import Path


class Config:
    def __init__(self, path: str = "data/config.json"):
        self.path = Path(path)
        self.data = json.loads(self.path.read_text(encoding="utf-8"))

    def get(self, *keys, default=None):
        node = self.data
        for k in keys:
            if not isinstance(node, dict) or k not in node:
                return default
            node = node[k]
        return node

    @property
    def impersonate(self) -> str:
        return self.get("tls", "impersonate", default="chrome150")

    @property
    def timeout(self) -> int:
        return self.get("tls", "timeout", default=30)

    @property
    def page_template(self) -> str:
        return self.get("http", "pageTemplate", default="https://boost.ink/{slug}")

    @property
    def origin(self) -> str:
        return self.get("http", "origin", default="https://boost.ink")

    @property
    def referer(self) -> str:
        return self.get("http", "referer", default="https://boost.ink/")

    @property
    def stepdelay(self) -> float:
        return float(self.get("unlock", "stepDelay", default=2.0))

    @property
    def host(self) -> str:
        return self.get("server", "host", default="0.0.0.0")

    @property
    def port(self) -> int:
        return int(self.get("server", "port", default=8002))
