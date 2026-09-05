class VehicleTrackingException(Exception):
    """Base exception class for application errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class EntityNotFoundException(VehicleTrackingException):
    def __init__(self, entity_name: str, entity_id: str | int):
        super().__init__(
            message=f"{entity_name} with identifier '{entity_id}' was not found.",
            status_code=404
        )

class ForbiddenAccessException(VehicleTrackingException):
    def __init__(self, detail: str = "Access forbidden. You are not authorized to access this resource."):
        super().__init__(message=detail, status_code=403)

class InvalidCredentialsException(VehicleTrackingException):
    def __init__(self, detail: str = "Incorrect email or password."):
        super().__init__(message=detail, status_code=401)
