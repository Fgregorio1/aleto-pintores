import os
import sys
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

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

    query = """
        SELECT conversion_action.id, conversion_action.name, conversion_action.type
        FROM conversion_action
    """
    response = ga_service.search(customer_id=customer_id, query=query)
    print("\n=== CONVERSION ACTIONS ===")
    for row in response:
        print(f"Name: {row.conversion_action.name}")
        print(f"  ID: {row.conversion_action.id}")
        print(f"  Type: {row.conversion_action.type_.name}\n")

if __name__ == "__main__":
    main()
