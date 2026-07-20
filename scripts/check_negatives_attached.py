"""Checks if the Shared Negative Keyword List is attached to active campaigns.

Run: .venv/bin/python scripts/check_negatives_attached.py
"""

import os
import sys

from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

REQUIRED = [
    "GOOGLE_ADS_DEVELOPER_TOKEN",
    "GOOGLE_ADS_CLIENT_ID",
    "GOOGLE_ADS_CLIENT_SECRET",
    "GOOGLE_ADS_REFRESH_TOKEN",
    "GOOGLE_ADS_LOGIN_CUSTOMER_ID",
    "GOOGLE_ADS_CUSTOMER_ID",
]
missing = [k for k in REQUIRED if not os.getenv(k)]
if missing:
    print("✗ Missing values in .env: " + ", ".join(missing))
    sys.exit(1)

config = {
    "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
    "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
    "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
    "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
    "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
    "use_proto_plus": True,
}

client = GoogleAdsClient.load_from_dict(config)
ga_service = client.get_service("GoogleAdsService")
customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")

query = """
    SELECT
      campaign.name,
      campaign_shared_set.shared_set,
      shared_set.name,
      shared_set.status
    FROM campaign_shared_set
    WHERE shared_set.status = 'ENABLED'
"""

print("Fetching attached negative lists...")
try:
    response = ga_service.search(customer_id=customer_id, query=query)
    rows = list(response)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

if not rows:
    print("⚠ No negative lists are attached to any campaigns!")
    sys.exit(0)

print(f"\nAttached lists:")
for row in rows:
    print(f"- Campaign: {row.campaign.name}")
    print(f"  Shared Set List Name: {row.shared_set.name}")
    print(f"  Shared Set Resource Name: {row.campaign_shared_set.shared_set}")
    print("-" * 50)
