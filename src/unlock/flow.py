import base64
import json
import re
import time
from urllib.parse import urlparse

from src.config import Config
from src.session.client import Client
from src.unlock.page import UnlockPage

trueflags = ("true",)

class Flow:
    def __init__(self, config: Config, client: Client, slug: str):
        self.config = config
        self.client = client
        self.slug = slug
        self.pageurl = config.page_template.format(slug=slug)

    def openpage(self) -> UnlockPage:
        response = self.client.get(self.pageurl)
        return UnlockPage(response.text)

    def quest(self, step: dict) -> dict:
        href = step["href"]
        host = urlparse(href).hostname or ""
        response = self.client.get(href)
        html = response.text
        payload = self.extractpayload(html)
        result = {
            "href": href,
            "host": host,
            "status": response.status_code,
            "router": None,
            "redirect": None,
            "passback": None,
        }
        if not payload:
            return result
        router = self.routerurl(href)
        body = self.buildbody(payload)
        routed = self.client.post(router, body, headers=self.routerheaders(href))
        text = routed.text.strip()
        result["router"] = router
        if text.startswith("http"):
            result["redirect"] = text
        else:
            result["redirect"] = self.findclick(text)
            if result["redirect"] is None and "passback" in text:
                result["passback"] = self.findpassback(text)
        return result

    def extractpayload(self, html: str) -> dict | None:
        match = re.search(r'atob\("([A-Za-z0-9+/=]+)"\)', html)
        token = match.group(1) if match else None
        if token is None:
            loose = re.findall(r'[A-Za-z0-9+/]{60,}={0,2}', html)
            for candidate in loose:
                try:
                    raw = base64.b64decode(candidate + "=" * (-len(candidate) % 4)).decode(
                        "utf-8", "replace"
                    )
                    data = json.loads(raw)
                except Exception:
                    continue
                if isinstance(data, dict) and "parameters" in data:
                    return data
            return None
        try:
            raw = base64.b64decode(token).decode("utf-8", "replace")
            return json.loads(raw)
        except Exception:
            return None

    def routerurl(self, href: str) -> str:
        parts = urlparse(href)
        return f"https://router.parklogic.com{parts.path}"

    def routerheaders(self, href: str) -> dict:
        parts = urlparse(href)
        origin = f"{parts.scheme}://{parts.netloc}"
        return {
            "Origin": origin,
            "Referer": origin + "/",
            "Accept": "*/*",
        }

    def buildbody(self, payload: dict) -> str:
        params = payload.setdefault("parameters", {})
        params["adBlockingDetected"] = False
        params["isIframe"] = False
        params["refererBrowser"] = self.config.referer
        params["timezoneBrowser"] = "Pacific/Auckland"
        params["timezoneOffset"] = -780
        params["webdriver"] = False
        params["gpu"] = None
        return json.dumps(payload, separators=(",", ":"))

    def findclick(self, html: str) -> str | None:
        match = re.search(r'href="(/[^"]+)"', html)
        if not match:
            return None
        path = re.sub(r"^\.", "", match.group(1))
        return "https://xml-v4.pushub.net" + path

    def findpassback(self, html: str) -> str | None:
        match = re.search(r'https://passback\.parklogic\.com/[^"\'<>\s]+', html)
        if match:
            return match.group(0)
        return None

    def run(self) -> dict:
        page = self.openpage()
        target = page.dest()
        steps = page.steps()
        trace = []
        if steps:
            for step in steps:
                trace.append(self.quest(step))
                time.sleep(self.config.stepdelay)
        return {
            "slug": self.slug,
            "source": self.pageurl,
            "destination": target,
            "steps": steps,
            "trace": trace,
        }
