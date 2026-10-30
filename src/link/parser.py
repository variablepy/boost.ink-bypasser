from urllib.parse import urlparse

class LinkParser:
    def __init__(self, url: str):
        self.url = url

    def slug(self) -> str:
        path = urlparse(self.url).path.strip("/")
        chunks = [c for c in path.split("/") if c]
        if not chunks:
            raise ValueError(f"cannot parse slug from {self.url!r}")
        return chunks[0]
