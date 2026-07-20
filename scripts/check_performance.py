"""Checks performance metrics for all campaigns over the last 24 hours.

Run: .venv/bin/python scripts/check_performance.py
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

# Query campaign metrics for today
query = """
    SELECT
      campaign.name,
      campaign.status,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions
    FROM campaign
    WHERE segments.date DURING TODAY
      AND campaign.status != 'REMOVED'
"""

print("Fetching today's campaign performance metrics...")
try:
    response = ga_service.search(customer_id=customer_id, query=query)
    rows = list(response)
except Exception as e:
    print(f"Error querying API: {e}")
    sys.exit(1)

if not rows:
    print("No campaign performance data returned for today. The campaigns might be paused, still in review, or data has not synced yet.")
    sys.exit(0)

print(f"\nPerformance breakdown for today:")
for row in rows:
    name = row.campaign.name
    status = row.campaign.status.name
    impressions = row.metrics.impressions
    clicks = row.metrics.clicks
    cost = row.metrics.cost_micros / 1_000_000.0
    conversions = row.metrics.conversions

    print(f"- Campaign: {name}")
    print(f"  Status: {status}")
    print(f"  Impressions: {impressions}")
    print(f"  Clicks: {clicks}")
    print(f"  Cost: €{cost:.2f}")
    print(f"  Conversions: {conversions}")
    print("-" * 30)
