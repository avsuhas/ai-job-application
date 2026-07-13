"""Local API security middleware (docs/12, docs/17 Phase 11).

The API is a local-first service. These middlewares keep it that way:
requests must originate from loopback, mutating requests must carry a
same-origin Origin/Referer (CSRF defense for a browser-hosted UI), and
every response carries conservative security headers including a strict CSP
that matches the self-contained inline dashboard.
"""

from __future__ import annotations

from urllib.parse import urlparse

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

_LOCAL_HOSTS = {"127.0.0.1", "::1", "localhost", "testserver", "testclient"}
_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

# The dashboard is fully self-contained (inline styles + scripts), so the CSP
# can forbid every external source while allowing the inline UI to run.
_CSP = (
    "default-src 'none'; "
    "script-src 'unsafe-inline'; "
    "style-src 'unsafe-inline'; "
    "connect-src 'self'; "
    "img-src 'self' data:; "
    "base-uri 'none'; "
    "form-action 'none'; "
    "frame-ancestors 'none'"
)

_SECURITY_HEADERS = {
    "Content-Security-Policy": _CSP,
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
}


def _client_is_local(request: Request) -> bool:
    client = request.client
    if client is None:
        return True  # ASGI test transports omit the client; treat as local
    return client.host in _LOCAL_HOSTS or client.host.startswith("127.")


def _host_is_local(request: Request) -> bool:
    host = (request.headers.get("host") or "").split(":")[0].lower()
    return not host or host in _LOCAL_HOSTS


class LocalOnlyMiddleware(BaseHTTPMiddleware):
    """Reject any request that does not originate from loopback."""

    async def dispatch(self, request: Request, call_next):
        if not _client_is_local(request) or not _host_is_local(request):
            return JSONResponse(
                status_code=403,
                content={
                    "error": {
                        "code": "local_only",
                        "message": "This service accepts requests from localhost only.",
                        "details": {},
                    }
                },
            )
        return await call_next(request)


class CSRFOriginMiddleware(BaseHTTPMiddleware):
    """For mutating requests, require a same-origin Origin/Referer header."""

    async def dispatch(self, request: Request, call_next):
        if request.method not in _SAFE_METHODS:
            origin = request.headers.get("origin") or request.headers.get("referer")
            if origin is not None:
                host = (urlparse(origin).hostname or "").lower()
                if host and host not in _LOCAL_HOSTS and not host.startswith("127."):
                    return JSONResponse(
                        status_code=403,
                        content={
                            "error": {
                                "code": "csrf_blocked",
                                "message": "Cross-origin request rejected.",
                                "details": {"origin": origin},
                            }
                        },
                    )
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        for header, value in _SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)
        return response
