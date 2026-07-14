"""Creates a Shared Negative Keyword List in Google Ads.

Run: .venv/bin/python scripts/create_negative_list.py
Reads creds from .env at the repo root.
"""

import os
import sys

from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Load .env variables
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

# Negative keywords list (Text, Match Type: 'BROAD', 'PHRASE', or 'EXACT')
NEGATIVES = [
    # Jobs / Employment
    ("empleo", "BROAD"),
    ("trabajo", "BROAD"),
    ("curriculum", "BROAD"),
    ("trabajar en", "PHRASE"),
    ("enviar cv", "PHRASE"),
    ("sueldo", "BROAD"),
    ("salario", "BROAD"),
    ("jobs", "BROAD"),
    ("careers", "BROAD"),
    # DIY / Information / Learning
    ("como pintar", "PHRASE"),
    ("como quitar", "PHRASE"),
    ("como se quita", "PHRASE"),
    ("how to paint", "PHRASE"),
    ("curso", "BROAD"),
    ("tutorial", "BROAD"),
    ("bricolaje", "BROAD"),
    ("hazlo tu mismo", "PHRASE"),
    ("diy", "BROAD"),
    ("foro", "BROAD"),
    ("opiniones de pintores", "PHRASE"),
    ("fotos", "BROAD"),
    ("imagenes", "BROAD"),
    # Retailers / Material stores (prevent bidding on brand searches)
    ("leroy merlin", "PHRASE"),
    ("bricomart", "PHRASE"),
    ("obramat", "PHRASE"),
    ("bricodepot", "PHRASE"),
    ("bauhaus", "PHRASE"),
    ("ikea", "PHRASE"),
    ("comprar pintura", "PHRASE"),
    ("tienda pintura", "PHRASE"),
    # Cheap / Low Budget
    ("gratis", "BROAD"),
    ("free", "BROAD"),
    ("barato", "BROAD"),
    ("barata", "BROAD"),
    # negatives do NOT match plurals/close variants — list them explicitly
    ("baratos", "BROAD"),
    ("baratas", "BROAD"),
    ("economico", "BROAD"),
    ("economica", "BROAD"),
    ("low cost", "PHRASE"),
    # Equipment / Tools (for DIYers)
    ("rodillo", "BROAD"),
    ("pistola de pintar", "PHRASE"),
    ("brocha", "BROAD"),
    ("escalera", "BROAD"),
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

    shared_set_service = client.get_service("SharedSetService")
    shared_criterion_service = client.get_service("SharedCriterionService")

    # 1. Create the Shared Set (Negative Keyword List)
    shared_set_operation = client.get_type("SharedSetOperation")
    shared_set = shared_set_operation.create
    shared_set.name = "Aleto Universal Negatives"
    shared_set.type_ = client.enums.SharedSetTypeEnum.NEGATIVE_KEYWORDS

    try:
        response = shared_set_service.mutate_shared_sets(
            customer_id=customer_id, operations=[shared_set_operation]
        )
        shared_set_resource_name = response.results[0].resource_name
        print(f"✓ Created Shared Negative Keyword List: {shared_set_resource_name}")
    except GoogleAdsException as ex:
        print(f"✗ Failed to create Shared Set: {ex}")
        for error in ex.failure.errors:
            print(f"\tError: {error.message}")
        sys.exit(1)

    # 2. Add negative keywords to the Shared Set
    shared_criteria_operations = []
    keyword_match_type_enum = client.enums.KeywordMatchTypeEnum

    for keyword_text, match_type in NEGATIVES:
        operation = client.get_type("SharedCriterionOperation")
        criterion = operation.create
        criterion.shared_set = shared_set_resource_name
        criterion.keyword.text = keyword_text
        
        if match_type == "EXACT":
            criterion.keyword.match_type = keyword_match_type_enum.EXACT
        elif match_type == "PHRASE":
            criterion.keyword.match_type = keyword_match_type_enum.PHRASE
        else:
            criterion.keyword.match_type = keyword_match_type_enum.BROAD

        shared_criteria_operations.append(operation)

    try:
        response = shared_criterion_service.mutate_shared_criteria(
            customer_id=customer_id, operations=shared_criteria_operations
        )
        print(f"✓ Added {len(response.results)} negative keywords to the list.")
    except GoogleAdsException as ex:
        print(f"✗ Failed to add negative keywords: {ex}")
        for error in ex.failure.errors:
            print(f"\tError: {error.message}")
        sys.exit(1)

if __name__ == "__main__":
    main()
