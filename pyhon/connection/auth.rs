```rust
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::error::Error;
use std::time::{Duration, SystemTime};
use reqwest::{Client, Response};
use regex::Regex;
use log::{error, info};
use url::form_urlencoded;
use url::Url;
use std::sync::Arc;
use tokio::sync::Mutex;

#[derive(Default, Serialize, Deserialize)]
struct HonLoginData {
    url: String,
    email: String,
    password: String,
    fw_uid: String,
    loaded: Option<HashMap<String, serde_json::Value>>,
}

#[derive(Default, Serialize, Deserialize)]
struct HonAuthData {
    access_token: String,
    refresh_token: String,
    cognito_token: String,
    id_token: String,
}

struct HonAuth {
    session: Arc<Mutex<Client>>,
    email: String,
    password: String,
    device: HonDevice,
    expires: SystemTime,
    auth: HonAuthData,
    login_data: HonLoginData,
}

impl HonAuth {
    const TOKEN_EXPIRES_AFTER_HOURS: u64 = 8;
    const TOKEN_EXPIRE_WARNING_HOURS: u64 = 7;

    pub fn new(session: Arc<Mutex<Client>>, email: String, password: String, device: HonDevice) -> Self {
        Self {
            session,
            email,
            password,
            device,
            expires: SystemTime::now(),
            auth: HonAuthData::default(),
            login_data: HonLoginData::default(),
        }
    }

    pub async fn authenticate(&mut self) -> Result<(), Box<dyn Error>> {
        self.clear();
        if !self.load_login().await? {
            return Err("Can't open login page".into());
        }
        let url = self.login().await?;
        if url.is_empty() || !self.get_token(&url).await? {
            return Err("Can't get token".into());
        }
        if !self.api_auth().await? {
            return Err("Can't get api token".into());
        }
        Ok(())
    }

    pub async fn refresh(&mut self) -> Result<bool, Box<dyn Error>> {
        let params = [
            ("client_id", consts::CLIENT_ID),
            ("refresh_token", &self.auth.refresh_token),
            ("grant_type", "refresh_token"),
        ];
        let response = self.session.lock().await.post(format!("{}/services/oauth2/token", consts::AUTH_API))
            .form(&params)
            .send()
            .await?;

        if response.status().is_client_error() || response.status().is_server_error() {
            self.error_logger(&response, false).await?;
            return Ok(false);
        }

        let data: HashMap<String, String> = response.json().await?;
        self.expires = SystemTime::now();
        self.auth.id_token = data["id_token"].clone();
        self.auth.access_token = data["access_token"].clone();
        self.api_auth().await
    }

    fn clear(&mut self) {
        // Clear cookies and reset auth data
        self.session.lock().await.cookie_jar.clear_domain(consts::AUTH_API.split('/').last().unwrap());
        self.auth = HonAuthData::default();
    }

    async fn load_login(&mut self) -> Result<bool, Box<dyn Error>> {
        let login_url = self.introduce().await?;
        let login_url = self.handle_redirects(&login_url).await?;
        self.login_url(&login_url).await
    }

    async fn introduce(&mut self) -> Result<String, Box<dyn Error>> {
        let redirect_uri = url::form_urlencoded::byte_serialize(format!("{}://mobilesdk/detect/oauth/done", consts::APP).as_bytes()).collect::<String>();
        let params = [
            ("response_type", "token+id_token"),
            ("client_id", consts::CLIENT_ID),
            ("redirect_uri", &redirect_uri),
            ("display", "touch"),
            ("scope", "api openid refresh_token web"),
            ("nonce", &self.generate_nonce()),
        ];
        let params_encoded = form_urlencoded::Serializer::new(String::new())
            .extend_pairs(&params)
            .finish();

        let url = format!("{}/services/oauth2/authorize/expid_Login?{}", consts::AUTH_API, params_encoded);
        let response = self.session.lock().await.get(&url).send().await?;
        let text = response.text().await?;
        self.expires = SystemTime::now();

        let re = Regex::new(r"url = '(.+?)'").unwrap();
        if let Some(caps) = re.captures(&text) {
            Ok(caps[1].to_string())
        } else if text.contains("oauth/done#access_token=") {
            self.parse_token_data(&text);
            return Err("No authentication needed".into());
        } else {
            self.error_logger(&response, true).await?;
            Err("Failed to load login".into())
        }
    }

    async fn handle_redirects(&self, login_url: &str) -> Result<String, Box<dyn Error>> {
        let redirect1 = self.manual_redirect(login_url).await?;
        let redirect2 = self.manual_redirect(&redirect1).await?;
        Ok(format!("{}&System=IoT_Mobile_App&RegistrationSubChannel=hOn", redirect2))
    }

    async fn manual_redirect(&self, url: &str) -> Result<String, Box<dyn Error>> {
        let response = self.session.lock().await.get(url).send().await?;
        if let Some(new_location) = response.headers().get("Location") {
            Ok(new_location.to_str()?.to_string())
        } else {
            self.error_logger(&response, true).await?;
            Err("No redirect location found".into())
        }
    }

    async fn login_url(&mut self, login_url: &str) -> Result<bool, Box<dyn Error>> {
        let headers = reqwest::header::HeaderMap::new();
        headers.insert("User-Agent", consts::USER_AGENT.parse()?);
        let response = self.session.lock().await.get(login_url).headers(headers).send().await?;
        let text = response.text().await?;

        let re = Regex::new(r#""fwuid":"(.*?)","loaded":(\{.*?})"#).unwrap();
        if let Some(caps) = re.captures(&text) {
            self.login_data.fw_uid = caps[1].to_string();
            self.login_data.loaded = Some(serde_json::from_str(&caps[2])?);
            self.login_data.url = login_url.replace(consts::AUTH_API, "");
            Ok(true)
        } else {
            self.error_logger(&response, true).await?;
            Ok(false)
        }
    }

    async fn login(&mut self) -> Result<String, Box<dyn Error>> {
        let start_url = self.login_data.url.split("startURL=").last().unwrap_or("");
        let action = json!({
            "id": "79;a",
            "descriptor": "apex://LightningLoginCustomController/ACTION$login",
            "callingDescriptor": "markup://c:loginForm",
            "params": {
                "username": self.login_data.email,
                "password": self.login_data.password,
                "startUrl": start_url,
            },
        });

        let data = json!({
            "message": { "actions": [action] },
            "aura.context": {
                "mode": "PROD",
                "fwuid": self.login_data.fw_uid,
                "app": "siteforce:loginApp2",
                "loaded": self.login_data.loaded,
                "dn": [],
                "globals": {},
                "uad": false,
            },
            "aura.pageURI": self.login_data.url,
            "aura.token": null,
        });

        let params = [("r", "3"), ("other.LightningLoginCustom.login", "1")];
        let response = self.session.lock().await.post(format!("{}/s/sfsites/aura", consts::AUTH_API))
            .header("Content-Type", "application/x-www-form-urlencoded")
            .body(form_urlencoded::Serializer::new(String::new())
                .extend_pairs(data.as_object().unwrap().iter().map(|(k, v)| (k.as_str(), &v)))
                .finish())
            .query(&params)
            .send()
            .await?;

        if response.status().is_success() {
            let result: HashMap<String, serde_json::Value> = response.json().await?;
            let url = result["events"][0]["attributes"]["values"]["url"].as_str().unwrap_or("").to_string();
            Ok(url)
        } else {
            self.error_logger(&response, true).await?;
            Ok(String::new())
        }
    }

    fn parse_token_data(&mut self, text: &str) -> bool {
        let access_token_re = Regex::new(r"access_token=(.*?)&").unwrap();
        let refresh_token_re = Regex::new(r"refresh_token=(.*?)&").unwrap();
        let id_token_re = Regex::new(r"id_token=(.*?)&").unwrap();

        if let Some(caps) = access_token_re.captures(text) {
            self.auth.access_token = caps[1].to_string();
        }
        if let Some(caps) = refresh_token_re.captures(text) {
            self.auth.refresh_token = caps[1].to_string();
        }
        if let Some(caps) = id_token_re.captures(text) {
            self.auth.id_token = caps[1].to_string();
        }
        self.auth.access_token.is_empty() || self.auth.refresh_token.is_empty() || self.auth.id_token.is_empty()
    }

    async fn get_token(&mut self, url: &str) -> Result<bool, Box<dyn Error>> {
        let response = self.session.lock().await.get(url).send().await?;
        if response.status().is_client_error() || response.status().is_server_error() {
            self.error_logger(&response, true).await?;
            return Ok(false);
        }

        let url_search: Vec<String> = Regex::new(r#"href\s*=\s*["'](.+?)["']"#).unwrap()
            .captures_iter(&response.text().await?)
            .filter_map(|caps| caps.get(1).map(|m| m.as_str().to_string()))
            .collect();

        if url_search.is_empty() {
            self.error_logger(&response, true).await?;
            return Ok(false);
        }

        let mut final_url = url_search[0].clone();
        if final_url.contains("ProgressiveLogin") {
            let response = self.session.lock().await.get(&final_url).send().await?;
            if response.status().is_client_error() || response.status().is_server_error() {
                self.error_logger(&response, true).await?;
                return Ok(false);
            }
            let url_search: Vec<String> = Regex::new(r#"href\s*=\s*["'](.*?)["']"#).unwrap()
                .captures_iter(&response.text().await?)
                .filter_map(|caps| caps.get(1).map(|m| m.as_str().to_string()))
                .collect();
            final_url = url_search[0].clone();
        }

        let final_url = format!("{}{}", consts::AUTH_API, final_url);
        let response = self.session.lock().await.get(&final_url).send().await?;
        if response.status().is_client_error() || response.status().is_server_error() {
            self.error_logger(&response, true).await?;
            return Ok(false);
        }

        if !self.parse_token_data(&response.text().await?) {
            self.error_logger(&response, true).await?;
            return Ok(false);
        }
        Ok(true)
    }

    async fn api_auth(&mut self) -> Result<bool, Box<dyn Error>> {
        let post_headers = reqwest::header::HeaderMap::new();
        post_headers.insert("id-token", self.auth.id_token.parse()?);
        let data = self.device.get();
        let response = self.session.lock().await.post(format!("{}/auth/v1/login", consts::API_URL))
            .headers(post_headers)
            .json(&data)
            .send()
            .await?;

        let json_data: HashMap<String, serde_json::Value> = response.json().await?;
        self.auth.cognito_token = json_data.get("cognitoUser").and_then(|v| v.get("Token")).and_then(|v| v.as_str()).unwrap_or("").to_string();

        if self.auth.cognito_token.is_empty() {
            error!("{:?}", json_data);
            return Err("Authentication error".into());
        }
        Ok(true)
    }

    async fn error_logger(&self, response: &Response, fail: bool) -> Result<(), Box<dyn Error>> {
        let mut output = String::from("hOn Authentication Error\n");
        for (i, (status, url)) in self.request.called_urls.iter().enumerate() {
            output.push_str(&format!(" {:2}     {} - {}\n", i + 1, status, url));
        }
        output.push_str(&format!("ERROR - {} - {}\n", response.status(), response.url()));
        output.push_str(&format!("{} Response {}\n{}\n{}", "=".repeat(15), "=".repeat(15), response.text().await?, "=".repeat(40)));
        error!("{}", output);
        if fail {
            return Err("Can't login".into());
        }
        Ok(())
    }

    fn generate_nonce() -> String {
        let nonce = rand::random::<[u8; 16]>();
        format!("{:x}-{:x}-{:x}-{:x}-{:x}", 
            u32::from_be_bytes(nonce[0..4].try_into().unwrap()),
            u32::from_be_bytes(nonce[4..8].try_into().unwrap()),
            u32::from_be_bytes(nonce[8..12].try_into().unwrap()),
            u32::from_be_bytes(nonce[12..16].try_into().unwrap()),
        )
    }

    fn check_token_expiration(&self, hours: u64) -> bool {
        let expiration_time = self.expires + Duration::from_secs(hours * 3600);
        SystemTime::now() >= expiration_time
    }

    fn token_is_expired(&self) -> bool {
        self.check_token_expiration(Self::TOKEN_EXPIRES_AFTER_HOURS)
    }

    fn token_expires_soon(&self) -> bool {
        self.check_token_expiration(Self::TOKEN_EXPIRE_WARNING_HOURS)
    }
}
```