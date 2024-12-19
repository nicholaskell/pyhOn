```rust
/// Custom error type for authentication errors.
#[derive(Debug)]
pub struct HonAuthenticationError;

impl std::fmt::Display for HonAuthenticationError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "HonAuthenticationError")
    }
}

impl std::error::Error for HonAuthenticationError {}

/// Custom error type for cases where no authentication is needed.
#[derive(Debug)]
pub struct HonNoAuthenticationNeeded;

impl std::fmt::Display for HonNoAuthenticationNeeded {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "HonNoAuthenticationNeeded")
    }
}

impl std::error::Error for HonNoAuthenticationNeeded {}

/// Custom error type for cases where no session exists.
#[derive(Debug)]
pub struct NoSessionException;

impl std::fmt::Display for NoSessionException {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "NoSessionException")
    }
}

impl std::error::Error for NoSessionException {}

/// Custom error type for cases where no authentication is found.
#[derive(Debug)]
pub struct NoAuthenticationException;

impl std::fmt::Display for NoAuthenticationException {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "NoAuthenticationException")
    }
}

impl std::error::Error for NoAuthenticationException {}

/// Custom error type for API errors.
#[derive(Debug)]
pub struct ApiError;

impl std::fmt::Display for ApiError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "ApiError")
    }
}

impl std::error::Error for ApiError {}
```