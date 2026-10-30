from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.config import Config
from src.link.parser import LinkParser
from src.session.client import Client
from src.unlock.flow import Flow

class BypassRequest(BaseModel):
    url: str
    proxy: str | None = None
    trace: bool = False


def reply(payload: dict, status: int = 200) -> JSONResponse:
    return JSONResponse(status_code=status, content=payload)

def createapp(config: Config) -> FastAPI:
    app = FastAPI(title="Boost.ink Bypass API", version="1.0")

    @app.post("/bypass")
    def bypass(req: BypassRequest):
        try:
            slug = LinkParser(req.url).slug()
        except ValueError as exc:
            return reply({"ok": False, "error": {"stage": "parse", "message": str(exc)}}, 400)
        client = Client(config, req.proxy)
        try:
            result = Flow(config, client, slug).run()
        except Exception as exc:
            return reply({"ok": False, "error": {"stage": "flow", "message": str(exc)}}, 502)
        payload = {
            "ok": bool(result.get("destination")),
            "result": {
                "destination": result.get("destination"),
                "steps": [s["title"] for s in result.get("steps") or []],
            },
        }
        if req.trace:
            payload["trace"] = result.get("trace")
        return reply(payload)

    return app