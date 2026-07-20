"""Checks all assets in the Google Ads account and prints their policy/approval status.

Useful for debugging campaign asset (sitelink, call, etc.) disapproval reasons programmatically.
Run: .venv/bin/python scripts/check_disapproved_assets.py
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

query_assets = """
    SELECT
      asset.id,
      asset.name,
      asset.type,
      asset.policy_summary.review_status,
      asset.policy_summary.approval_status,
      asset.policy_summary.policy_topic_entries
    FROM asset
"""

print("Fetching assets...")
response = ga_service.search(customer_id=customer_id, query=query_assets)
assets = list(response)
print(f"Found {len(assets)} assets.\n")

for row in assets:
    asset_id = row.asset.id
    asset_name = row.asset.name
    asset_type = row.asset.type_.name
    review_status = row.asset.policy_summary.review_status.name
    approval_status = row.asset.policy_summary.approval_status.name
    policy_topics = row.asset.policy_summary.policy_topic_entries

    print(f"Asset: ID={asset_id} | Name={asset_name or 'N/A'} | Type={asset_type}")
    print(f"Review: {review_status} | Approval: {approval_status}")
    if policy_topics:
        print("Policy Topic Entries:")
        for topic in policy_topics:
            print(f"  - Topic: {topic.topic} | Type: {topic.type_}")
    print("-" * 50)
