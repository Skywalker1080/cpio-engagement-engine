import os
import json
import logging
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import webbrowser

from src.config import LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, LINKEDIN_REDIRECT_URI, LINKEDIN_TOKEN_PATH

logger = logging.getLogger(__name__)

class LinkedInClient:
    def __init__(self):
        self.client_id = LINKEDIN_CLIENT_ID
        self.client_secret = LINKEDIN_CLIENT_SECRET
        self.redirect_uri = LINKEDIN_REDIRECT_URI
        self.token_file = LINKEDIN_TOKEN_PATH
        self.access_token = None
        self.person_urn = None
        self.load_token()

    def load_token(self):
        if self.token_file.exists():
            try:
                data = json.loads(self.token_file.read_text())
                self.access_token = data.get("access_token")
                self.person_urn = data.get("person_urn")
                if self.access_token:
                    logger.info("Loaded existing LinkedIn access token.")
            except Exception as e:
                logger.error(f"Failed to load token file: {e}")

    def save_token(self):
        if self.access_token:
            data = {"access_token": self.access_token, "person_urn": self.person_urn}
            self.token_file.write_text(json.dumps(data))
            logger.info("Saved new LinkedIn access token.")

    def authenticate(self):
        """Perform 3-legged OAuth for LinkedIn."""
        if self.access_token and self.get_profile():
            logger.info("Already authenticated!")
            return True

        if not self.client_id or not self.client_secret:
            logger.error("LinkedIn Client ID or Secret is missing in `.env`.")
            return False

        # Start a local server to catch the redirect
        server_address = ('', 8080)
        auth_code = [None]

        class AuthHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

            def do_GET(self):
                parsed = urllib.parse.urlparse(self.path)
                query = urllib.parse.parse_qs(parsed.query)
                if 'code' in query:
                    auth_code[0] = query['code'][0]
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b"<html><body><h1>Authentication successful!</h1><p>You can close this tab and return to the terminal.</p></body></html>")
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"No code parameter found.")

        httpd = HTTPServer(server_address, AuthHandler)

        # Scopes required for posting
        scopes = "openid profile w_member_social email"
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": "random_string",
            "scope": scopes
        }
        auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(params)}"
        
        print("\n" + "="*50)
        print("Opening browser for LinkedIn Authentication...")
        print("If it doesn't open, click this link:")
        print(auth_url)
        print("="*50 + "\n")
        
        webbrowser.open(auth_url)
        
        print("Waiting for callback on http://localhost:8080/callback ...")
        while auth_code[0] is None:
            httpd.handle_request()
            
        print("Authorization code received! Exchanging for token...")
        
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        data = {
            "grant_type": "authorization_code",
            "code": auth_code[0],
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        res = requests.post(token_url, data=data)
        if res.status_code == 200:
            self.access_token = res.json().get("access_token")
            self.get_profile()  # Fetch and save person_urn
            self.save_token()
            return True
        else:
            logger.error(f"Failed to get access token: {res.text}")
            return False

    def get_profile(self):
        """Fetch the authenticated user's URN."""
        if not self.access_token:
            return False
            
        url = "https://api.linkedin.com/v2/userinfo"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            self.person_urn = f"urn:li:person:{data.get('sub')}"
            return True
        return False

    def post_content(self, text: str):
        """Create a text post on LinkedIn."""
        if not self.access_token or not self.person_urn:
            logger.error("Not authenticated or person URN unknown.")
            return False

        # Using LinkedIn's Posts API
        url = "https://api.linkedin.com/rest/posts"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "LinkedIn-Version": "202604",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        payload = {
            "author": self.person_urn,
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False
        }
        
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 201:
            postId = res.headers.get("x-restli-id", "")
            logger.info(f"Successfully posted to LinkedIn! Post ID: {postId}")
            return True
        else:
            logger.error(f"Failed to post. Status: {res.status_code}, Error: {res.text}")
            return False
