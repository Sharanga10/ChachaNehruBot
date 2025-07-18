import requests
import webbrowser

# Replace with your app's credentials
client_id = "VmJqcE5JUHk5Zmd1M2l3VGtnQko6MTpjaQ"
client_secret = "wSGCiwFyo4fDy5CBCSa5CtZK_g9-Yg20KZrZxUu4R4OVxCEvZg"
redirect_uri = "https://localhost:3000"  # Must match X developer portal

# Step 1: Get the authorization URL
auth_url = "https://twitter.com/i/oauth2/authorize"
scopes = "tweet.read users.read offline.access"
state = "state_xyz"
code_challenge = "challenge"
code_challenge_method = "plain"

auth_params = {
    "response_type": "code",
    "client_id": client_id,
    "redirect_uri": redirect_uri,
    "scope": scopes,
    "state": state,
    "code_challenge": code_challenge,
    "code_challenge_method": code_challenge_method
}

print("\n🔗 Visit this URL in browser to authorize:\n")
print(f"{auth_url}?{'&'.join([f'{k}={v}' for k, v in auth_params.items()])}")
print("\n📋 After authorization, copy the 'code' from the redirect URL and paste below.\n")

webbrowser.open(f"{auth_url}?{'&'.join([f'{k}={v}' for k, v in auth_params.items()])}")

# Step 2: Exchange code for tokens
authorization_code = input("Paste the 'code' from URL: ").strip()

token_url = "https://api.twitter.com/2/oauth2/token"

token_data = {
    "code": authorization_code,
    "grant_type": "authorization_code",
    "client_id": client_id,
    "redirect_uri": redirect_uri,
    "code_verifier": "challenge",
}

response = requests.post(token_url, data=token_data, auth=(client_id, client_secret))

print("\n✅ Response:")
print(response.status_code)
print(response.json())