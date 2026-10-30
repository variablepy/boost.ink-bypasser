# boost.ink bypass

> a fast bypasser for boost.ink. reads the destination straight out of the unlock script.

**written by [cheapai.gay](https://cheapai.gay/) / deepthroat ai.**

---

## what it does

- takes a `boost.ink/<slug>` url
- parses the step blocks and the `bufpsvdhmjybvgfncqfa` base64 attribute
- decodes the destination url directly from the page
- walks each quest step through `router.parklogic.com` and records the redirect / passback

> [!WARNING]
> boost.ink will quickly patch this bypass if they are smart enough. the destination is currently shipped to the client in a base64 attribute on the unlock script, and the quest router returns the next hop as plain text. the moment they move that behind a server-side check, or add a signature on the router call, this breaks. treat it as a snapshot, not a permanent solution.

---

## how it works

```mermaid
flowchart TD
    A[GET boost.ink/slug] --> B[parse page]
    B --> C[decode bufpsvdhmjybvgfncqfa]
    C --> D[destination url]
    B --> E[collect step blocks]
    E --> F[GET quest page]
    F --> G[decode atob payload]
    G --> H[POST router.parklogic.com/path]
    H --> I{response}
    I -->|starts with http| J[redirect url]
    I -->|html| K[click url / passback]
```

| step | operation | notes |
|------|-----------|-------|
| 1 | `GET boost.ink/<slug>` | locker page |
| 2 | read attribute | base64 destination on `unlock.js` tag |
| 3 | parse `.step_block` | quest links + titles |
| 4 | `GET` quest page | contains base64 json in `atob(...)` |
| 5 | `POST router.parklogic.com` | fingerprint fields filled in |
| 6 | read response | plain url, click href or passback |

---

## stack

- `fastapi` for the http layer
- `curl_cffi` with `chrome150` tls fingerprint
- user-supplied proxy per request

---

## layout

```text
.
├── data/
│   └── config.json
├── src/
│   ├── config.py
│   ├── link/
│   │   └── parser.py
│   ├── session/
│   │   └── client.py
│   ├── unlock/
│   │   ├── page.py
│   │   └── flow.py
│   └── web/
│       └── api.py
└── entry.py
```

---

## install

```bash
pip install fastapi uvicorn curl_cffi
```

---

## run

```bash
python entry.py
```

---

## usage

### request

```bash
curl -X POST http://127.0.0.1:8002/bypass \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"https://boost.ink/xc8\"}"
```

optional fields: `proxy` (e.g. `http://user:pass@host:port`) and `trace` (`true` to include the step trace).

### response

```json
{
  "ok": true,
  "result": {
    "destination": "https://setquest.io/en/quest/gCYIYF47bq/",
    "steps": ["Join my Discord"]
  }
}
```

with `trace: true` you also get each quest hop:

```json
{
  "trace": [
    {
      "href": "https://setquest.io/en/quest/gCYIYF47bq/",
      "host": "setquest.io",
      "status": 200,
      "router": "https://router.parklogic.com/en/quest/gCYIYF47bq/",
      "redirect": "https://xml-v4.pushub.net/click?i=lzgqI2yKptM_0",
      "passback": null
    }
  ]
}
```

---

## config

`data/config.json`:

```json
{
  "tls": {
    "impersonate": "chrome150",
    "timeout": 30
  },
  "http": {
    "pageTemplate": "https://boost.ink/{slug}",
    "origin": "https://boost.ink",
    "referer": "https://boost.ink/"
  },
  "unlock": {
    "stepDelay": 2.0
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8002
  }
}
```

---

## limitations

- only handles single-slug boost.ink links
- quest pages that change their router endpoint will break the step walk
- destination can be empty if the locker serves a step-only page with no target
- **boost.ink will quickly patch this bypass if they are smart enough**

---

## credits

written by **[cheapai.gay](https://cheapai.gay/)** / **deepthroat ai**.