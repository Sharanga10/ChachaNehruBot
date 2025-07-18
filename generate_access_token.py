import os
import requests
import webbrowser
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTH_URL = "https://twitter.com/i/oauth2/authorize"
TOKEN_URL = "https://api.twitter.com/2/oauth2/token"

SCOPES = [
    "tweet.read", "tweet.write", "users.read",
    "offline.access"
]

STATE = "chacha123"  # Random string to verify state
PORT = 8888
auth_code = None

# Step 1: Build Authorization URL
def build_auth_url():
    scope_param = "%20".join(SCOPES)
    url = (
        f"{AUTH_URL}?"
        f"response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={scope_param}&state={STATE}"
        f"&code_challenge=challenge&code_challenge_method=plain"
    )
    return url

# Step 2: Start Local Server to Capture Redirect
class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)
        if "code" in params and "state" in params:
            if params["state"][0] == STATE:
                auth_code = params["code"][0]
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Authorization complete. You can close this tab.")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Invalid state. Possible CSRF.")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing code or state.")

def start_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🔁 Waiting for login redirect on http://127.0.0.1:{PORT}/callback ...")
        httpd.handle_request()

# Step 3: Exchange Code for Tokens
def get_tokens(code):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "code_verifier": "challenge"
    }
    response = requests.post(TOKEN_URL, data=data, auth=(CLIENT_ID, CLIENT_SECRET))
    if response.status_code == 200:
        return response.json()
    else:
        print("❌ Token exchange failed:", response.text)
        return None

# Step 4: Save tokens to .env
def update_env(tokens):
    with open(".env", "a") as f:
        f.write(f'\nBEARER_TOKEN={tokens["access_token"]}')
        f.write(f'\nREFRESH_TOKEN={tokens["refresh_token"]}')
        f.write(f'\nEXPIRES_IN={tokens["expires_in"]}')
    print("✅ Tokens saved to .env")

# 🔃 Main flow
if __name__ == "__main__":
    print("🌐 Opening browser for Twitter login...")
    webbrowser.open(build_auth_url())
    start_server()

    if auth_code:
        print("🔐 Authorization code received. Fetching tokens...")
        tokens = get_tokens(auth_code)
        if tokens:
            update_env(tokens)
        else:
            print("❌ Failed to retrieve tokens.")
    else:
        print("❌ Authorization code not captured.")