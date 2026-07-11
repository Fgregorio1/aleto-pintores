"""Authenticate with Google Ads: OAuth flow → refresh token → .env.

Run: .venv/bin/python scripts/authenticate_google.py

Reads the OAuth client from docs/google-ads/credentials-google-cloud-aleto.json,
opens your browser to sign in (use the Google account that owns the Ads account),
then writes GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET and
GOOGLE_ADS_REFRESH_TOKEN into .env at the repo root.

No secrets are printed to the terminal.
"""

import json
import os
import re

from google_auth_oauthlib.flow import InstalledAppFlow

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CREDS_PATH = os.path.join(ROOT, "docs", "google-ads", "credentials-google-cloud-aleto.json")
ENV_PATH = os.path.join(ROOT, ".env")
SCOPES = ["https://www.googleapis.com/auth/adwords"]


def upsert_env(text: str, key: str, value: str) -> str:
    """Replace `KEY=...` in .env text, or append if absent."""
    pattern = re.compile(rf"^{key}=.*$", re.MULTILINE)
    line = f"{key}={value}"
    if pattern.search(text):
        return pattern.sub(line, text)
    return text.rstrip("\n") + "\n" + line + "\n"


def main() -> None:
    with open(CREDS_PATH) as f:
        client_config = json.load(f)
    installed = client_config["installed"]

    print("Opening browser — sign in with the Google account that owns the Ads account…")
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")

    if not creds.refresh_token:
        raise SystemExit("✗ No refresh token returned. Re-run and make sure you approve access.")

    with open(ENV_PATH) as f:
        env_text = f.read()
    env_text = upsert_env(env_text, "GOOGLE_ADS_CLIENT_ID", installed["client_id"])
    env_text = upsert_env(env_text, "GOOGLE_ADS_CLIENT_SECRET", installed["client_secret"])
    env_text = upsert_env(env_text, "GOOGLE_ADS_REFRESH_TOKEN", creds.refresh_token)
    with open(ENV_PATH, "w") as f:
        f.write(env_text)

    print("✓ Authenticated. client_id, client_secret and refresh_token written to .env")
    print("  (values not shown — check with: grep -c GOOGLE_ADS .env)")


if __name__ == "__main__":
    main()
