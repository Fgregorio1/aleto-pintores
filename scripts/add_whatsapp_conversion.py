"""Creates the "WhatsApp click" Google Ads conversion action (docs/04 Phase B).

Secondary/observation action (primary_for_goal=False): it must inform keyword
evaluation without polluting the Conversions column that Smart Bidding will
optimize against — "Submit lead form" and "Calls from ads (60s+)" stay primary.
Fired from the site by Attribution.astro on wa.me clicks (gtag event, see
src/data/business.ts googleAdsWhatsappLabel).

Idempotent: prints the existing action's label if already present.

Run: .venv/bin/python scripts/add_whatsapp_conversion.py
"""

import os
import re
import sys

from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

NAME = "WhatsApp click"


def get_client():
    return GoogleAdsClient.load_from_dict({
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
        "use_proto_plus": True,
    })


def print_label(client, customer_id):
    svc = client.get_service("GoogleAdsService")
    rows = list(svc.search(customer_id=customer_id, query=f"""
        SELECT conversion_action.resource_name, conversion_action.id,
               conversion_action.status, conversion_action.primary_for_goal,
               conversion_action.tag_snippets
        FROM conversion_action
        WHERE conversion_action.name = '{NAME}'"""))
    if not rows:
        return False
    ca = rows[0].conversion_action
    print(f"• Action exists: {ca.resource_name} (status {ca.status.name}, "
          f"primary_for_goal={ca.primary_for_goal})")
    for snip in ca.tag_snippets:
        m = re.search(r"send_to['\"]?\s*:\s*['\"](AW-[\d]+/[\w-]+)['\"]", snip.event_snippet)
        if m:
            print(f"✓ send_to: {m.group(1)}")
            print(f"✓ label:   {m.group(1).split('/')[1]}")
            return True
    print("⚠ No label found in tag snippets — inspect in the UI")
    return True


def main():
    client = get_client()
    customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")

    if print_label(client, customer_id):
        return

    op = client.get_type("ConversionActionOperation")
    ca = op.create
    ca.name = NAME
    ca.type_ = client.enums.ConversionActionTypeEnum.WEBPAGE
    ca.category = client.enums.ConversionActionCategoryEnum.CONTACT
    ca.status = client.enums.ConversionActionStatusEnum.ENABLED
    ca.primary_for_goal = False
    ca.counting_type = client.enums.ConversionActionCountingTypeEnum.ONE_PER_CLICK
    ca.click_through_lookback_window_days = 30
    svc = client.get_service("ConversionActionService")
    resp = svc.mutate_conversion_actions(customer_id=customer_id, operations=[op])
    print(f"✓ Created: {resp.results[0].resource_name}")
    if not print_label(client, customer_id):
        sys.exit(1)


if __name__ == "__main__":
    main()
