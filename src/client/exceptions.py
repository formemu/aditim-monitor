"""
Custom exceptions for the ADITIM Monitor Client.
"""

class AditimClientError(Exception):
    """Base exception class for the client."""
    pass

class APIError(AditimClientError):
    """Raised for errors related to API communication."""
    def __init__(self, message="Ошибка API", status_code=None):
        self.status_code = status_code
        super().__init__(f"{message} (Status Code: {status_code})" if status_code else message)

class UIError(AditimClientError):
    """Raised for errors related to the user interface."""
    pass

class DataLoadError(AditimClientError):
    """Raised when data loading fails."""
    pass
