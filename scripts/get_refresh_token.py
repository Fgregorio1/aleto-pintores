"""Generates a Google Ads refresh token.

Run: python3 scripts/get_refresh_token.py
Opens browser → sign in with the Google account that owns the Ads account →
"Allow" → token is printed to your terminal. Paste it into .env as
GOOGLE_ADS_REFRESH_TOKEN.

Dependency: pip3 install google-auth-oauthlib
"""

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/adwords"]

client_id = input("Paste your CLIENT_ID: ").strip()
client_secret = input("Paste your CLIENT_SECRET: ").strip()

client_config = {
    "installed": {
        "client_id": client_id,
        "client_secret": client_secret,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"],
    }
}

flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")

print("\n\n=== YOUR REFRESH TOKEN ===")
print(creds.refresh_token)
print("==========================\n")
print("Paste this into .env as GOOGLE_ADS_REFRESH_TOKEN")
