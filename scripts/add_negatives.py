"""Adds new negative keywords to the existing 'Aleto Universal Negatives' list.

Run: .venv/bin/python scripts/add_negatives.py
"""

import os
import sys

from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

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

# The new negative keywords to add (targeting plurals and informational "como" searches)
NEW_NEGATIVES = [
    ("baratos", "BROAD"),
    ("baratas", "BROAD"),
    ("economicos", "BROAD"),
    ("economicas", "BROAD"),
    ("como", "BROAD"),
    ("cómo", "BROAD"),
    ("paso a paso", "PHRASE"),
    ("tutoriales", "BROAD"),
    ("casero", "BROAD"),
    ("hacer", "BROAD"),
]

def main():
    config = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
        "use_proto_plus": True,
    }

    client = GoogleAdsClient.load_from_dict(config)
    customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    ga_service = client.get_service("GoogleAdsService")
    shared_criterion_service = client.get_service("SharedCriterionService")

    # 1. Find the shared set resource name for "Aleto Universal Negatives"
    query = """
        SELECT shared_set.resource_name, shared_set.name
        FROM shared_set
        WHERE shared_set.name = 'Aleto Universal Negatives'
          AND shared_set.status = 'ENABLED'
    """
    
    print("Finding the negative keyword list...")
    response = ga_service.search(customer_id=customer_id, query=query)
    rows = list(response)
    if not rows:
        print("✗ Could not find active 'Aleto Universal Negatives' list. Please run create_negative_list.py first.")
        sys.exit(1)
        
    shared_set_rn = rows[0].shared_set.resource_name
    print(f"✓ Found list: {shared_set_rn}")

    # 2. Get existing keywords in the list to avoid duplicates
    query_existing = f"""
        SELECT shared_criterion.keyword.text, shared_criterion.keyword.match_type
        FROM shared_criterion
        WHERE shared_criterion.shared_set = '{shared_set_rn}'
    """
    response_existing = ga_service.search(customer_id=customer_id, query=query_existing)
    existing_keywords = {r.shared_criterion.keyword.text.lower() for r in response_existing}
    
    # 3. Filter out new negatives that already exist
    to_add = [item for item in NEW_NEGATIVES if item[0].lower() not in existing_keywords]
    
    if not to_add:
        print("All of these negative keywords are already present in the list. Nothing to add.")
        sys.exit(0)

    # 4. Add the keywords
    operations = []
    keyword_match_type_enum = client.enums.KeywordMatchTypeEnum

    for text, match_type in to_add:
        op = client.get_type("SharedCriterionOperation")
        criterion = op.create
        criterion.shared_set = shared_set_rn
        criterion.keyword.text = text
        
        if match_type == "EXACT":
            criterion.keyword.match_type = keyword_match_type_enum.EXACT
        elif match_type == "PHRASE":
            criterion.keyword.match_type = keyword_match_type_enum.PHRASE
        else:
            criterion.keyword.match_type = keyword_match_type_enum.BROAD
            
        operations.append(op)

    print(f"Adding {len(operations)} new negative keywords to the list...")
    try:
        resp = shared_criterion_service.mutate_shared_criteria(
            customer_id=customer_id, operations=operations
        )
        print(f"✓ Successfully added {len(resp.results)} keywords:")
        for text, match_type in to_add:
            print(f"  - '{text}' ({match_type})")
    except GoogleAdsException as ex:
        print(f"✗ Failed to add negative keywords: {ex}")
        for error in ex.failure.errors:
            print(f"\tError: {error.message}")
        sys.exit(1)

if __name__ == "__main__":
    main()
