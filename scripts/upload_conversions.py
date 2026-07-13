import csv
import os
import sys
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

def upload_conversions(csv_path, conversion_action_id):
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
    conversion_upload_service = client.get_service("ConversionUploadService")

    operations = []
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gclid = row.get("gclid", "").strip()
            value = row.get("value", "").strip()
            time = row.get("time", "").strip() # Format: yyyy-mm-dd hh:mm:ss+tz (e.g. 2026-07-13 14:00:00+02:00)
            
            if not gclid or not value or not time:
                continue

            click_conversion = client.get_type("ClickConversion")
            click_conversion.conversion_action = f"customers/{customer_id}/conversionActions/{conversion_action_id}"
            click_conversion.gclid = gclid
            click_conversion.conversion_value = float(value)
            click_conversion.conversion_date_time = time
            click_conversion.currency_code = "EUR"

            operations.append(click_conversion)

    if not operations:
        print("No valid conversion rows found in CSV.")
        return

    request = client.get_type("UploadClickConversionsRequest")
    request.customer_id = customer_id
    request.conversions.extend(operations)
    request.partial_failure = True

    try:
        response = conversion_upload_service.upload_click_conversions(request=request)
        
        # Check partial failures
        if response.partial_failure_error:
            print(f"✗ Partial failure encountered: {response.partial_failure_error.message}")
        
        for i, result in enumerate(response.results):
            if result.gclid:
                print(f"✓ Uploaded conversion: GCLID {result.gclid} at {result.conversion_date_time}")
            else:
                print(f"✗ Row {i+1} failed to upload.")
    except GoogleAdsException as ex:
        print(f"✗ Failed to upload conversions: {ex}")
        for error in ex.failure.errors:
            print(f"\tError: {error.message}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/upload_conversions.py <csv_path> <conversion_action_id>")
        sys.exit(1)
    
    upload_conversions(sys.argv[1], sys.argv[2])
