```python
import json
import re
import asyncio
from typing import Dict, Optional, Any
from aiohttp import ClientSession, ClientResponse
from urllib.parse import urlencode
import logging
import time
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HonLoginData:
    def __init__(self):
        self.url: str = ""
        self.email: str = ""
        self.password: str = ""
        self.fw_uid: str = ""
        self.loaded: Optional[Dict[str, Any]] = None

class HonAuthData:
    def __init__(self):
        self.access_token: str = ""
        self.refresh_token: str = ""
        self.cognito_token: str = ""
        self.id_token: str = ""

class HonAuth:
    TOKEN_EXPIRES_AFTER_HOURS = 8
    TOKEN_EXPIRE_WARNING_HOURS = 7

    def __init__(self, session: ClientSession, email: str, password: str, device: Any):
        self.session = session
        self.email = email
        self.password = password
        self.device = device
        self.expires = time.time()
        self.auth = HonAuthData()
        self.login_data = HonLoginData()

    async def authenticate(self) -> None:
        self.clear()
        if not await self.load_login():
            raise Exception("Can't open login page")
        url = await self.login()
        if not url or not await self.get_token(url):
            raise Exception("Can't get token")
        if not await self.api_auth():
            raise Exception("Can't get api token")

    async def refresh(self) -> bool:
        params = {
            "client_id": consts.CLIENT_ID,
            "refresh_token": self.auth.refresh_token,
            "grant_type": "refresh_token"
        }
        async with self.session.post(f"{consts.AUTH_API}/services/oauth2/token", data=params) as response:
            if response.status >= 400:
                await self.error_logger(response, False)
                return False

            data = await response.json()
            self.expires = time.time()
            self.auth.id_token = data["id_token"]
            self.auth.access_token = data["access_token"]
            return await self.api_auth()

    def clear(self) -> None:
        # Clear cookies and reset auth data
        self.session.cookie_jar.clear_domain(consts.AUTH_API.split('/')[-1])
        self.auth = HonAuthData()

    async def load_login(self) -> bool:
        login_url = await self.introduce()
        login_url = await self.handle_redirects(login_url)
        return await self.login_url(login_url)

    async def introduce(self) -> str:
        redirect_uri = urlencode({"response_type": "token+id_token",
                                   "client_id": consts.CLIENT_ID,
                                   "redirect_uri": f"{consts.APP}://mobilesdk/detect/oauth/done",
                                   "display": "touch",
                                   "scope": "api openid refresh_token web",
                                   "nonce": self.generate_nonce()})
        url = f"{consts.AUTH_API}/services/oauth2/authorize/expid_Login?{redirect_uri}"
        async with self.session.get(url) as response:
            text = await response.text()
            self.expires = time.time()

            match = re.search(r"url = '(.+?)'", text)
            if match:
                return match.group(1)
            elif "oauth/done#access_token=" in text:
                self.parse_token_data(text)
                raise Exception("No authentication needed")
            else:
                await self.error_logger(response, True)
                raise Exception("Failed to load login")

    async def handle_redirects(self, login_url: str) -> str:
        redirect1 = await self.manual_redirect(login_url)
        redirect2 = await self.manual_redirect(redirect1)
        return f"{redirect2}&System=IoT_Mobile_App&RegistrationSubChannel=hOn"

    async def manual_redirect(self, url: str) -> str:
        async with self.session.get(url) as response:
            if "Location" in response.headers:
                return response.headers["Location"]
            else:
                await self.error_logger(response, True)
                raise Exception("No redirect location found")

    async def login_url(self, login_url: str) -> bool:
        headers = {"User-Agent": consts.USER_AGENT}
        async with self.session.get(login_url, headers=headers) as response:
            text = await response.text()

            match = re.search(r#""fwuid":"(.*?)","loaded":(\{.*?})"#, text)
            if match:
                self.login_data.fw_uid = match.group(1)
                self.login_data.loaded = json.loads(match.group(2))
                self.login_data.url = login_url.replace(consts.AUTH_API, "")
                return True
            else:
                await self.error_logger(response, True)
                return False

    async def login(self) -> str:
        start_url = self.login_data.url.split("startURL=")[-1]
        action = {
            "id": "79;a",
            "descriptor": "apex://LightningLoginCustomController/ACTION$login",
            "callingDescriptor": "markup://c:loginForm",
            "params": {
                "username": self.login_data.email,
                "password": self.login_data.password,
                "startUrl": start_url,
            },
        }

        data = {
            "message": {"actions": [action]},
            "aura.context": {
                "mode": "PROD",
                "fwuid": self.login_data.fw_uid,
                "app": "siteforce:loginApp2",
                "loaded": self.login_data.loaded,
                "dn": [],
                "globals": {},
                "uad": False,
            },
            "aura.pageURI": self.login_data.url,
            "aura.token": None,
        }

        params = {"r": "3", "other.LightningLoginCustom.login": "1"}
        async with self.session.post(f"{consts.AUTH_API}/s/sfsites/aura", 
                                      headers={"Content-Type": "application/x-www-form-urlencoded"},
                                      data=urlencode(data)) as response:
            if response.status == 200:
                result = await response.json()
                return result["events"][0]["attributes"]["values"]["url"]
            else:
                await self.error_logger(response, True)
                return ""

    def parse_token_data(self, text: str) -> bool:
        access_token_re = re.compile(r"access_token=(.*?)&")
        refresh_token_re = re.compile(r"refresh_token=(.*?)&")
        id_token_re = re.compile(r"id_token=(.*?)&")

        if (match := access_token_re.search(text)):
            self.auth.access_token = match.group(1)
        if (match := refresh_token_re.search(text)):
            self.auth.refresh_token = match.group(1)
        if (match := id_token_re.search(text)):
            self.auth.id_token = match.group(1)

        return not (self.auth.access_token and self.auth.refresh_token and self.auth.id_token)

    async def get_token(self, url: str) -> bool:
        async with self.session.get(url) as response:
            if response.status >= 400:
                await self.error_logger(response, True)
                return False

            url_search = re.findall(r'href\s*=\s*["\'](.+?)["\']', await response.text())
            if not url_search:
                await self.error_logger(response, True)
                return False

            final_url = url_search[0]
            if "ProgressiveLogin" in final_url:
                async with self.session.get(final_url) as response:
                    if response.status >= 400:
                        await self.error_logger(response, True)
                        return False
                    url_search = re.findall(r'href\s*=\s*["\'](.*?)["\']', await response.text())
                    final_url = url_search[0]

            final_url = f"{consts.AUTH_API}{final_url}"
            async with self.session.get(final_url) as response:
                if response.status >= 400:
                    await self.error_logger(response, True)
                    return False

                if not self.parse_token_data(await response.text()):
                    await self.error_logger(response, True)
                    return False
            return True

    async def api_auth(self) -> bool:
        post_headers = {"id-token": self.auth.id_token}
        data = self.device.get()
        async with self.session.post(f"{consts.API_URL}/auth/v1/login", headers=post_headers, json=data) as response:
            json_data = await response.json()
            self.auth.cognito_token = json_data.get("cognitoUser", {}).get("Token", "")

            if not self.auth.cognito_token:
                logger.error(json_data)
                raise Exception("Authentication error")
            return True

    async def error_logger(self, response: ClientResponse, fail: bool) -> None:
        output = "hOn Authentication Error\n"
        # Assuming self.request.called_urls is defined somewhere
        for i, (status, url) in enumerate(self.request.called_urls):
            output += f" {i + 1:2}     {status} - {url}\n"
        output += f"ERROR - {response.status} - {response.url}\n"
        output += f"{'=' * 15} Response {'=' * 15}\n{await response.text()}\n{'=' * 40}"
        logger.error(output)
        if fail:
            raise Exception("Can't login")

    @staticmethod
    def generate_nonce() -> str:
        nonce = random.getrandbits(128).to_bytes(16, 'big')
        return f"{int.from_bytes(nonce[0:4], 'big')}-{int.from_bytes(nonce[4:8], 'big')}-{int.from_bytes(nonce[8:12], 'big')}-{int.from_bytes(nonce[12:16], 'big')}"

    def check_token_expiration(self, hours: int) -> bool:
        expiration_time = self.expires + hours * 3600
        return time.time() >= expiration_time

    def token_is_expired(self) -> bool:
        return self.check_token_expiration(self.TOKEN_EXPIRES_AFTER_HOURS)

    def token_expires_soon(self) -> bool:
        return self.check_token_expiration(self.TOKEN_EXPIRE_WARNING_HOURS)
```