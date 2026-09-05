import logging
from fastapi import Request, status, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.custom_exceptions import VehicleTrackingException

logger = logging.getLogger("fastapi_backend")

def register_exception_handlers(app: FastAPI):
    """
    Registers centralized exception handlers for the FastAPI application.
    Enforces standardized error responses with 'error': {'code': ..., 'message': ...}.
    Ensures SQL queries, stack traces, and internal paths are NEVER leaked to clients.
    """

    @app.exception_handler(VehicleTrackingException)
    async def vehicle_tracking_exception_handler(request: Request, exc: VehicleTrackingException):
        logger.warning(f"Domain exception [{exc.error_code}]: {exc.message} (Path: {request.url.path})")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message
                },
                "detail": exc.message
            }
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        error_code = "HTTP_ERROR"
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            error_code = "AUTHENTICATION_FAILED"
        elif exc.status_code == status.HTTP_403_FORBIDDEN:
            error_code = "AUTHORIZATION_FAILED"
        elif exc.status_code == status.HTTP_404_NOT_FOUND:
            error_code = "RESOURCE_NOT_FOUND"
        elif exc.status_code == status.HTTP_400_BAD_REQUEST:
            error_code = "BAD_REQUEST"

        message = str(exc.detail) if isinstance(exc.detail, str) else "HTTP Request Error"
        logger.warning(f"HTTP exception [{error_code} - {exc.status_code}]: {message} (Path: {request.url.path})")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": error_code,
                    "message": message
                },
                "detail": exc.detail
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error on path {request.url.path}: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request payload or query parameters."
                },
                "detail": exc.errors()
            }
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # Development log securely records technical details / traceback
        logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)

        # Production response NEVER leaks SQL queries, stack traces, credentials, or file paths
        safe_message = "An internal server error occurred. Please try again later."
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": safe_message
                },
                "detail": safe_message
            }
        )
