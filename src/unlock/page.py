import base64
import re
from html import unescape

class UnlockPage:
    def __init__(self, html: str):
        self.html = html

    def dest(self) -> str | None:
        match = re.search(
            r'unlock\.js[^>]*bufpsvdhmjybvgfncqfa="([A-Za-z0-9+/=]+)"',
            self.html,
        )
        if not match:
            return None
        raw = base64.b64decode(match.group(1)).decode("utf-8", "replace")
        return raw.strip() or None

    def steps(self) -> list[dict]:
        pattern = re.compile(
            r'<a class="step_block" href="([^"]+)"[^>]*>.*?<h2>(.*?)</h2>.*?<p>(.*?)</p>',
            re.S,
        )
        out = []
        for href, title, desc in pattern.findall(self.html):
            out.append(
                {
                    "href": unescape(href),
                    "title": unescape(re.sub(r"<[^>]+>", "", title)).strip(),
                    "description": unescape(re.sub(r"<[^>]+>", "", desc)).strip(),
                }
            )
        return out

    def completed(self) -> bool:
        return 'class="complete_btn" disabled' not in self.html
