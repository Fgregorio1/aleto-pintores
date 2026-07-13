"""Creates sitelink assets and links them to each campaign.

Reads the SITELINKS spec from build_campaigns.py (6 per campaign, all URLs
verified live). Idempotent: reuses an existing asset with the same link text
and skips campaign links that already exist.

Run: .venv/bin/python scripts/add_sitelinks.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from build_campaigns import SITELINKS, get_client, search

MAX_LINK_TEXT = 25
MAX_DESC = 35


def validate():
    ok = True
    for campaign, links in SITELINKS.items():
        for sl in links:
            if len(sl["text"]) > MAX_LINK_TEXT:
                print(f"✗ Link text >{MAX_LINK_TEXT} chars ({len(sl['text'])}): {sl['text']}")
                ok = False
            for key in ("d1", "d2"):
                if len(sl[key]) > MAX_DESC:
                    print(f"✗ Description >{MAX_DESC} chars ({len(sl[key])}): {sl[key]}")
                    ok = False
        if len(links) < 2:
            print(f"✗ {campaign}: needs at least 2 sitelinks")
            ok = False
    if not ok:
        sys.exit(1)
    print("✓ All sitelink copy within limits")


def ensure_asset(client, customer_id, sl):
    escaped = sl["text"].replace("'", "\\'")
    rows = search(
        client,
        customer_id,
        "SELECT asset.resource_name FROM asset "
        "WHERE asset.type = 'SITELINK' "
        f"AND asset.sitelink_asset.link_text = '{escaped}'",
    )
    if rows:
        return rows[0].asset.resource_name, False
    op = client.get_type("AssetOperation")
    asset = op.create
    asset.final_urls.append(sl["url"])
    asset.sitelink_asset.link_text = sl["text"]
    asset.sitelink_asset.description1 = sl["d1"]
    asset.sitelink_asset.description2 = sl["d2"]
    svc = client.get_service("AssetService")
    resp = svc.mutate_assets(customer_id=customer_id, operations=[op])
    return resp.results[0].resource_name, True


def main():
    validate()
    client = get_client()
    customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    ca_svc = client.get_service("CampaignAssetService")

    for campaign_name, links in SITELINKS.items():
        rows = search(
            client,
            customer_id,
            "SELECT campaign.resource_name FROM campaign "
            f"WHERE campaign.name = '{campaign_name}' "
            "AND campaign.status != 'REMOVED'",
        )
        if not rows:
            print(f"⚠ Campaign not found, skipping: {campaign_name}")
            continue
        campaign_rn = rows[0].campaign.resource_name
        print(f"\n=== {campaign_name} ===")

        linked = {
            r.campaign_asset.asset
            for r in search(
                client,
                customer_id,
                "SELECT campaign_asset.asset FROM campaign_asset "
                f"WHERE campaign_asset.campaign = '{campaign_rn}' "
                "AND campaign_asset.field_type = 'SITELINK' "
                "AND campaign_asset.status != 'REMOVED'",
            )
        }

        ops = []
        for sl in links:
            asset_rn, created = ensure_asset(client, customer_id, sl)
            tag = "created" if created else "exists"
            if asset_rn in linked:
                print(f"  • {sl['text']} (asset {tag}, already linked)")
                continue
            op = client.get_type("CampaignAssetOperation")
            ca = op.create
            ca.campaign = campaign_rn
            ca.asset = asset_rn
            ca.field_type = client.enums.AssetFieldTypeEnum.SITELINK
            ops.append(op)
            print(f"  ✓ {sl['text']} (asset {tag}, linking)")
        if ops:
            ca_svc.mutate_campaign_assets(customer_id=customer_id, operations=ops)
            print(f"  ✓ {len(ops)} sitelinks linked to campaign")

    print("\nDone.")


if __name__ == "__main__":
    main()
