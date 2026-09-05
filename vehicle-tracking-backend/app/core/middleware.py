from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.config import settings

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware attaching production HTTP security headers to all responses.
    Prevents MIME-sniffing, clickjacking, and XSS attacks.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
        return response

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware rejecting request payloads exceeding configured size thresholds (MAX_REQUEST_SIZE_BYTES).
    Prevents buffer overflow & payload flooding Denial of Service (DoS) attacks.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        content_length = request.headers.get("Content-Length")
        if content_length:
            try:
                length = int(content_length)
                if length > settings.MAX_REQUEST_SIZE_BYTES:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "error": {
                                "code": "PAYLOAD_TOO_LARGE",
                                "message": f"Request payload exceeds maximum allowed size of {settings.MAX_REQUEST_SIZE_BYTES} bytes."
                            },
                            "detail": "Request payload too large."
                        }
                    )
            except ValueError:
                pass

        return await call_next(request)
