"""Discovers your Google Ads account IDs and writes them into .env.

Run: .venv/bin/python scripts/discover_accounts.py

Requires GOOGLE_ADS_DEVELOPER_TOKEN to be set in .env (the string shown in the
MCC's API Center right after submitting the application — works for this call
even while approval is pending). Uses the OAuth credentials already in .env.

Lists every Ads account your Google login can access, identifies which is the
manager (MCC) and which is the client account, and fills in
GOOGLE_ADS_LOGIN_CUSTOMER_ID / GOOGLE_ADS_CUSTOMER_ID.
"""

import os
import re
import sys

from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(ROOT, ".env")
load_dotenv(ENV_PATH)

if not os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"):
    sys.exit("✗ GOOGLE_ADS_DEVELOPER_TOKEN is empty in .env — paste the token from the API Center first.")

config = {
    "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
    "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
    "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
    "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
    "use_proto_plus": True,
}

client = GoogleAdsClient.load_from_dict(config)
customer_service = client.get_service("CustomerService")
accessible = customer_service.list_accessible_customers()
ids = [r.split("/")[-1] for r in accessible.resource_names]
print(f"Accounts accessible to this login: {ids}")

ga_service = client.get_service("GoogleAdsService")
managers, clients_ = [], []
for cid in ids:
    try:
        rows = ga_service.search(
            customer_id=cid,
            query="SELECT customer.id, customer.descriptive_name, customer.manager, customer.test_account FROM customer",
        )
        for row in rows:
            kind = "MCC" if row.customer.manager else "client"
            test = " (TEST)" if row.customer.test_account else ""
            print(f"  · {cid} — {row.customer.descriptive_name or '(no name)'} [{kind}]{test}")
            (managers if row.customer.manager else clients_).append(cid)
    except Exception as e:  # token pending approval can still fail per-account queries
        print(f"  · {cid} — (details unavailable: {type(e).__name__})")


def upsert_env(text: str, key: str, value: str) -> str:
    pattern = re.compile(rf"^{key}=.*$", re.MULTILINE)
    line = f"{key}={value}"
    return pattern.sub(line, text) if pattern.search(text) else text.rstrip("\n") + "\n" + line + "\n"


if len(managers) == 1 and len(clients_) == 1:
    with open(ENV_PATH) as f:
        env_text = f.read()
    env_text = upsert_env(env_text, "GOOGLE_ADS_LOGIN_CUSTOMER_ID", managers[0])
    env_text = upsert_env(env_text, "GOOGLE_ADS_CUSTOMER_ID", clients_[0])
    with open(ENV_PATH, "w") as f:
        f.write(env_text)
    print(f"\n✓ Written to .env: LOGIN_CUSTOMER_ID={managers[0]} (MCC), CUSTOMER_ID={clients_[0]} (client)")
else:
    print("\n! Couldn't unambiguously pick MCC + client from the list above.")
    print("  Set GOOGLE_ADS_LOGIN_CUSTOMER_ID (the MCC) and GOOGLE_ADS_CUSTOMER_ID (the ads account) in .env manually.")
