import os
from dotenv import load_dotenv

# Load workspace .env
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

yaml_path = os.path.expanduser("~/google-ads.yaml")

yaml_content = f"""# Google Ads API Credentials - Generated automatically
developer_token: "{os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", "")}"
client_id: "{os.getenv("GOOGLE_ADS_CLIENT_ID", "")}"
client_secret: "{os.getenv("GOOGLE_ADS_CLIENT_SECRET", "")}"
refresh_token: "{os.getenv("GOOGLE_ADS_REFRESH_TOKEN", "")}"
login_customer_id: "{os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")}"
use_proto_plus: true
"""

with open(yaml_path, "w", encoding="utf-8") as f:
    f.write(yaml_content)

print(f"✓ Successfully generated: {yaml_path}")
