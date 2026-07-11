#!/usr/bin/env python3
"""One-time Google Ads OAuth consent flow (loopback, stdlib only).

Starts a local server, opens the Google consent screen, captures the
authorization code, exchanges it for a refresh token and appends the
Google Ads credentials to .env. Prints status; never prints secrets.
"""
import json
import secrets
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLIENT_FILE = ROOT / "google-oauth-client.json"
ENV_FILE = ROOT / ".env"
PORT = 8765
SCOPE = "https://www.googleapis.com/auth/adwords"

client = json.loads(CLIENT_FILE.read_text())["installed"]
state = secrets.token_urlsafe(16)
redirect_uri = f"http://localhost:{PORT}"

auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
    "client_id": client["client_id"],
    "redirect_uri": redirect_uri,
    "response_type": "code",
    "scope": SCOPE,
    "access_type": "offline",
    "prompt": "consent",
    "state": state,
})

print(f"AUTH_URL: {auth_url}", flush=True)
print("Waiting for browser consent...", flush=True)

code_holder: dict = {}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        ok = "code" in q and q.get("state", [""])[0] == state
        if ok:
            code_holder["code"] = q["code"][0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        msg = (
            "✅ Autenticación completada. Puedes cerrar esta pestaña y volver a Claude."
            if ok
            else "❌ Falta el código o el state no coincide. Vuelve a intentarlo."
        )
        self.wfile.write(f"<h2 style='font-family:sans-serif'>{msg}</h2>".encode())

    def log_message(self, *args):  # silence request logging
        pass


server = HTTPServer(("localhost", PORT), Handler)
while "code" not in code_holder:
    server.handle_request()
server.server_close()
print("Code received, exchanging for tokens...", flush=True)

data = urllib.parse.urlencode({
    "code": code_holder["code"],
    "client_id": client["client_id"],
    "client_secret": client["client_secret"],
    "redirect_uri": redirect_uri,
    "grant_type": "authorization_code",
}).encode()
resp = json.load(urllib.request.urlopen(
    urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
))

refresh = resp.get("refresh_token")
if not refresh:
    raise SystemExit(f"No refresh_token in response (keys: {list(resp)})")

env = ENV_FILE.read_text() if ENV_FILE.exists() else ""
if "GOOGLE_ADS_REFRESH_TOKEN" in env:
    import re
    env = re.sub(r"GOOGLE_ADS_REFRESH_TOKEN=.*", f"GOOGLE_ADS_REFRESH_TOKEN={refresh}", env)
else:
    env += (
        "\n# Google Ads API (OAuth client in google-oauth-client.json)\n"
        f"GOOGLE_ADS_CLIENT_ID={client['client_id']}\n"
        f"GOOGLE_ADS_CLIENT_SECRET={client['client_secret']}\n"
        f"GOOGLE_ADS_REFRESH_TOKEN={refresh}\n"
    )
ENV_FILE.write_text(env)
print("SUCCESS: refresh token saved to .env", flush=True)
