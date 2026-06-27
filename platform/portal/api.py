import os
import json
from urllib.request import urlopen, Request
from urllib.parse import urlencode

GOVERNANCE_API = os.getenv("GOVERNANCE_API_URL", "http://localhost:8100")


def api_get(path, params=None):
    try:
        url = f"{GOVERNANCE_API}{path}"
        if params:
            url += "?" + urlencode(params)
        req = Request(url)
        with urlopen(req, timeout=3) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return []


def api_post(path, data=None, params=None):
    try:
        url = f"{GOVERNANCE_API}{path}"
        if params:
            url += "?" + urlencode(params)
        body = json.dumps(data).encode() if data else None
        headers = {"Content-Type": "application/json"} if data else {}
        req = Request(url, data=body, headers=headers, method="POST")
        with urlopen(req, timeout=3) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return None
