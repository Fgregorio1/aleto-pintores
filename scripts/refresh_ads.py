"""Replaces the RSAs in each ad group with the current copy in build_campaigns.py.

RSAs are immutable in the Google Ads API, so "editing" means: create a new
PAUSED RSA from the CAMPAIGNS spec, then remove the old ones — but only ads
with zero impressions (guard against deleting anything with history).

Idempotent: an ad group whose existing RSA already matches the spec's headline
set exactly is skipped.

Run: .venv/bin/python scripts/refresh_ads.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from build_campaigns import CAMPAIGNS, add_rsa, get_client, search

MAX_HEADLINE = 30
MAX_DESCRIPTION = 90


def validate_copy():
    ok = True
    for spec in CAMPAIGNS:
        for ag in spec["ad_groups"]:
            for h in ag["headlines"]:
                if len(h) > MAX_HEADLINE:
                    print(f"✗ Headline >{MAX_HEADLINE} chars ({len(h)}): {h}")
                    ok = False
            for d in ag["descriptions"]:
                if len(d) > MAX_DESCRIPTION:
                    print(f"✗ Description >{MAX_DESCRIPTION} chars ({len(d)}): {d}")
                    ok = False
            if not 3 <= len(ag["headlines"]) <= 15:
                print(f"✗ {ag['name']}: needs 3-15 headlines, has {len(ag['headlines'])}")
                ok = False
            if not 2 <= len(ag["descriptions"]) <= 4:
                print(f"✗ {ag['name']}: needs 2-4 descriptions, has {len(ag['descriptions'])}")
                ok = False
    if not ok:
        sys.exit(1)
    print("✓ All copy within RSA limits")


def main():
    validate_copy()
    client = get_client()
    customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    svc = client.get_service("AdGroupAdService")

    for spec in CAMPAIGNS:
        for ag_spec in spec["ad_groups"]:
            rows = search(
                client,
                customer_id,
                "SELECT ad_group.resource_name FROM ad_group "
                f"WHERE ad_group.name = '{ag_spec['name']}' "
                "AND campaign.status != 'REMOVED'",
            )
            if not rows:
                print(f"⚠ Ad group not found, skipping: {ag_spec['name']}")
                continue
            ag_rn = rows[0].ad_group.resource_name

            existing = search(
                client,
                customer_id,
                "SELECT ad_group_ad.resource_name, ad_group_ad.ad.responsive_search_ad.headlines, "
                "metrics.impressions FROM ad_group_ad "
                f"WHERE ad_group_ad.ad_group = '{ag_rn}' "
                "AND ad_group_ad.status != 'REMOVED' "
                "AND ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD'",
            )

            target = list(ag_spec["headlines"])
            up_to_date = [
                r for r in existing
                if [h.text for h in r.ad_group_ad.ad.responsive_search_ad.headlines] == target
            ]
            stale = [r for r in existing if r not in up_to_date]

            if up_to_date and not stale:
                print(f"• {ag_spec['name']}: RSA already matches spec, skipping")
                continue

            if not up_to_date:
                add_rsa(client, customer_id, ag_rn, ag_spec)
                print(f"✓ {ag_spec['name']}: new RSA created (PAUSED)")

            for r in stale:
                if r.metrics.impressions > 0:
                    print(f"  ⚠ keeping old RSA with {r.metrics.impressions} impressions: "
                          f"{r.ad_group_ad.resource_name}")
                    continue
                op = client.get_type("AdGroupAdOperation")
                op.remove = r.ad_group_ad.resource_name
                svc.mutate_ad_group_ads(customer_id=customer_id, operations=[op])
                print(f"  ✓ removed old zero-impression RSA")

    print("\nDone. New RSAs are PAUSED like everything else.")


if __name__ == "__main__":
    main()
