import os

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles

app = FastAPI()

CHAT_UPSTREAM = os.environ.get("CHAT_UPSTREAM", "").rstrip("/")

_HOP_BY_HOP = frozenset(
    {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
    }
)


@app.middleware("http")
async def proxy_chat_to_gwchat(request: Request, call_next):
    """When CHAT_UPSTREAM is set (e.g. http://gwchat:3000), serve /chat* from gwchat."""
    if not CHAT_UPSTREAM or not request.url.path.startswith("/chat"):
        return await call_next(request)

    target = CHAT_UPSTREAM + request.url.path
    if request.url.query:
        target += "?" + str(request.url.query)

    body = await request.body()
    out_headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in _HOP_BY_HOP and k.lower() != "host"
    }
    host = CHAT_UPSTREAM.removeprefix("http://").removeprefix("https://").split("/")[0]
    out_headers["host"] = host

    async with httpx.AsyncClient(follow_redirects=False) as client:
        try:
            r = await client.request(
                request.method,
                target,
                content=body,
                headers=out_headers,
                timeout=httpx.Timeout(120.0),
            )
        except httpx.RequestError:
            return Response(
                content=b"Chat service unavailable",
                status_code=502,
                media_type="text/plain",
            )

    resp_headers = {
        k: v
        for k, v in r.headers.items()
        if k.lower() not in _HOP_BY_HOP | {"content-encoding", "transfer-encoding"}
    }
    return Response(content=r.content, status_code=r.status_code, headers=resp_headers)


app.mount("/", StaticFiles(directory="site", html=True), name="site")
