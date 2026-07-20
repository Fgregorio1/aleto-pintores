"""Checks all ads in the Google Ads account and prints their policy/approval status.

Useful for debugging campaign disapproval reasons programmatically.
Run: .venv/bin/python scripts/check_disapproved_ads.py
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
      ad_group.name,
      ad_group_ad.ad.id,
      ad_group_ad.status,
      ad_group_ad.policy_summary.review_status,
      ad_group_ad.policy_summary.approval_status,
      ad_group_ad.policy_summary.policy_topic_entries
    FROM ad_group_ad
    WHERE ad_group_ad.status != 'REMOVED'
"""

print("Fetching ads and their policy statuses...")
response = ga_service.search(customer_id=customer_id, query=query)

rows = list(response)
if not rows:
    print("No ads found in the account.")
    sys.exit(0)

print(f"\nFound {len(rows)} ads. Checking policy details:\n")

for row in rows:
    campaign_name = row.campaign.name
    ad_group_name = row.ad_group.name
    ad_id = row.ad_group_ad.ad.id
    ad_status = row.ad_group_ad.status.name
    review_status = row.ad_group_ad.policy_summary.review_status.name
    approval_status = row.ad_group_ad.policy_summary.approval_status.name
    policy_topics = row.ad_group_ad.policy_summary.policy_topic_entries

    print(f"Campaign: {campaign_name}")
    print(f"Ad Group: {ad_group_name}")
    print(f"Ad ID: {ad_id} | Status: {ad_status}")
    print(f"Review Status: {review_status} | Approval Status: {approval_status}")
    
    if policy_topics:
        print("Policy Topic Entries:")
        for topic in policy_topics:
            print(f"  - Topic: {topic.topic}")
            print(f"    Type: {topic.type_}")
            if topic.evidences:
                print("    Evidences:")
                for evidence in topic.evidences:
                    # Depending on evidence type, some fields might be populated
                    if evidence.website_common_detail:
                        print(f"      - Website detail: {evidence.website_common_detail.page_urls}")
                    if evidence.text_list:
                        print(f"      - Text: {evidence.text_list.texts}")
                    if evidence.destination_not_working:
                        print(f"      - Destination not working: URL={evidence.destination_not_working.expanded_url}, Device={evidence.destination_not_working.device}")
    else:
        print("No policy topic entries.")
    print("-" * 50)
