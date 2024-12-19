```python
import asyncio
import aiohttp
from aiohttp import ClientSession
from typing import Optional

class NoSessionException(Exception):
    """Custom error type for session-related issues."""
    def __str__(self):
        return "No session available"

class ConnectionHandler:
    """A handler for managing HTTP connections."""
    
    def __init__(self, session: Optional[ClientSession] = None):
        """
        Creates a new `ConnectionHandler`.

        Args:
            session: An optional `aiohttp.ClientSession`.
        """
        self.headers = {
            "User-Agent": "Your User Agent",
            "Content-Type": "application/json"
        }
        self.session = session
        self.create_session = session is None

    async def create(self) -> ClientSession:
        """Creates a new session if one does not already exist."""
        if self.create_session:
            self.session = ClientSession(headers=self.headers)
        return self.session

    async def close(self):
        """Closes the session if it was created by this handler."""
        if self.create_session and self.session:
            await self.session.close()
            self.session = None

    async def get_session(self) -> ClientSession:
        """Gets a reference to the session, or raises an error if none exists."""
        if self.session is None:
            raise NoSessionException
        return self.session

    async def get(self, url: str) -> aiohttp.ClientResponse:
        """Asynchronously performs a GET request."""
        session = await self.get_session()
        async with session.get(url) as response:
            if response.status != 200:
                raise NoSessionException
            return response

    async def post(self, url: str) -> aiohttp.ClientResponse:
        """Asynchronously performs a POST request."""
        session = await self.get_session()
        async with session.post(url) as response:
            if response.status != 200:
                raise NoSessionException
            return response
```

### Explanation:
- The `ConnectionHandler` class manages an HTTP client session using the `aiohttp` library.
- The `NoSessionException` class is a custom error type to handle cases where no session is available.
- The `__init__` method initializes the handler, optionally accepting an `aiohttp.ClientSession`.
- The `create` method initializes a new client session if one does not already exist.
- The `close` method cleans up the session if it was created by this handler.
- The `get` and `post` methods perform asynchronous HTTP requests, returning the response or raising an error if the session is not available.