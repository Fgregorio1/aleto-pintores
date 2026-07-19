"""One-command OAuth re-auth for the Google Ads API.

The OAuth app lives in "Testing" mode on Google Cloud, so refresh tokens are
revoked every 7 days. Until the app is published to "In production"
(Cloud Console → APIs & Services → OAuth consent screen → Publish app),
re-run this weekly when scripts/MCP start failing with invalid_grant.

Reads CLIENT_ID/SECRET from .env, opens the browser for the Google sign-in
(the only manual step), then rewrites GOOGLE_ADS_REFRESH_TOKEN in .env and
regenerates ~/google-ads.yaml for the MCP server.

Run: .venv/bin/python scripts/refresh_oauth_token.py
"""

import os
import re
import subprocess
import sys

from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

ROOT = os.path.join(os.path.dirname(__file__), "..")
ENV_PATH = os.path.abspath(os.path.join(ROOT, ".env"))
load_dotenv(ENV_PATH)

client_id = os.getenv("GOOGLE_ADS_CLIENT_ID")
client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET")
if not client_id or not client_secret:
    print("✗ GOOGLE_ADS_CLIENT_ID / GOOGLE_ADS_CLIENT_SECRET missing from .env")
    sys.exit(1)

flow = InstalledAppFlow.from_client_config(
    {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    },
    scopes=["https://www.googleapis.com/auth/adwords"],
)
creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")

if not creds.refresh_token:
    print("✗ No refresh token returned — re-run and make sure you approve access")
    sys.exit(1)

with open(ENV_PATH, "r", encoding="utf-8") as f:
    env = f.read()
new_line = f"GOOGLE_ADS_REFRESH_TOKEN={creds.refresh_token}"
if re.search(r"^GOOGLE_ADS_REFRESH_TOKEN=.*$", env, flags=re.M):
    env = re.sub(r"^GOOGLE_ADS_REFRESH_TOKEN=.*$", new_line, env, flags=re.M)
else:
    env = env.rstrip("\n") + "\n" + new_line + "\n"
with open(ENV_PATH, "w", encoding="utf-8") as f:
    f.write(env)
print("✓ .env updated with the new refresh token")

subprocess.run(
    [sys.executable, os.path.join(os.path.dirname(__file__), "generate_google_ads_yaml.py")],
    check=True,
)
print("✓ Done — scripts and the google-ads MCP are re-authenticated "
      "(restart the Claude Code session to reload the MCP if needed)")
