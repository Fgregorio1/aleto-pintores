"""Checks search terms that triggered clicks today.

Useful for proactive negative keyword optimization.
Run: .venv/bin/python scripts/check_search_terms.py
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

# Query search terms
query = """
    SELECT
      campaign.name,
      ad_group.name,
      search_term_view.search_term,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros
    FROM search_term_view
    WHERE segments.date DURING TODAY
"""

print("Fetching today's search term report...")
try:
    response = ga_service.search(customer_id=customer_id, query=query)
    rows = list(response)
except Exception as e:
    print(f"Error querying API: {e}")
    sys.exit(1)

if not rows:
    print("No search term data available for today yet. (Google Ads search term reports often have a 12-24 hour sync delay).")
    sys.exit(0)

print(f"\nSearch terms triggered today:")
for row in rows:
    campaign_name = row.campaign.name
    ad_group_name = row.ad_group.name
    search_term = row.search_term_view.search_term
    impressions = row.metrics.impressions
    clicks = row.metrics.clicks
    cost = row.metrics.cost_micros / 1_000_000.0

    print(f"- Campaign: {campaign_name} | Ad Group: {ad_group_name}")
    print(f"  Search Term: '{search_term}'")
    print(f"  Impressions: {impressions} | Clicks: {clicks} | Cost: €{cost:.2f}")
    print("-" * 50)
