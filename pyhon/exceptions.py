```python
class HonAuthenticationError(Exception):
    """Custom error type for authentication errors."""
    
    def __str__(self):
        return "HonAuthenticationError"


class HonNoAuthenticationNeeded(Exception):
    """Custom error type for cases where no authentication is needed."""
    
    def __str__(self):
        return "HonNoAuthenticationNeeded"


class NoSessionException(Exception):
    """Custom error type for cases where no session exists."""
    
    def __str__(self):
        return "NoSessionException"


class NoAuthenticationException(Exception):
    """Custom error type for cases where no authentication is found."""
    
    def __str__(self):
        return "NoAuthenticationException"


class ApiError(Exception):
    """Custom error type for API errors."""
    
    def __str__(self):
        return "ApiError"
```