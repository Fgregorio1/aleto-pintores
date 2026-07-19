"""2026-07-19 optimization pass (approved plan, see git history):

1. Spanish campaign budget €15 → €10/day (tight budget, focus on results)
2. Pause the English expat campaign (14 imps / 1 click in 5 days, 80% rank-lost)
3. Pause keyword "pintores madrid" PHRASE (2.6% CTR vs 8-11% on service terms)
4. Negatives: DIY products, unoffered services, research, out-of-area towns
5. Geo: add Boadilla del Monte + Tres Cantos (search terms proved demand)
6. Zona keywords for the two new towns

Idempotent: every mutation checks current state first.

Run: .venv/bin/python scripts/optimize_2026_07_19.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from build_campaigns import get_client, resolve_geo_targets, search

ES_CAMPAIGN = "Aleto Pintores - Madrid (Spanish)"
EN_CAMPAIGN = "Aleto Pintores - Expat Madrid (English)"
NEW_BUDGET_MICROS = 10_000_000
NEGATIVE_LIST_NAME = "Aleto Universal Negatives"

NEW_NEGATIVES = [
    ("pasta", "BROAD"),          # DIY product searches
    ("espatulas", "BROAD"),
    ("espátulas", "BROAD"),
    ("sin lijar", "PHRASE"),     # DIY method research
    ("muebles", "BROAD"),        # furniture painting — not offered
    ("merece la pena", "PHRASE"),
    ("arganda", "BROAD"),        # outside service area
    ("ciempozuelos", "BROAD"),
]

NEW_GEO_NAMES = ["Boadilla del Monte", "Tres Cantos"]
NEW_ZONA_KEYWORDS = [("pintores boadilla", "PHRASE"), ("pintores tres cantos", "PHRASE")]


def campaign_rn(client, cid, name):
    rows = search(client, cid,
                  f"SELECT campaign.resource_name, campaign.status FROM campaign WHERE campaign.name = '{name}'")
    return (rows[0].campaign.resource_name, rows[0].campaign.status.name) if rows else (None, None)


def main():
    client = get_client()
    cid = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    es_rn, _ = campaign_rn(client, cid, ES_CAMPAIGN)
    if not es_rn:
        print(f"✗ Campaign not found: {ES_CAMPAIGN}")
        sys.exit(1)

    # 1. Budget €10/day
    rows = search(client, cid,
                  "SELECT campaign_budget.resource_name, campaign_budget.amount_micros "
                  f"FROM campaign WHERE campaign.resource_name = '{es_rn}'")
    b = rows[0].campaign_budget
    if b.amount_micros == NEW_BUDGET_MICROS:
        print(f"• Budget already €{NEW_BUDGET_MICROS/1e6:.0f}/day")
    else:
        op = client.get_type("CampaignBudgetOperation")
        op.update.resource_name = b.resource_name
        op.update.amount_micros = NEW_BUDGET_MICROS
        op.update_mask.paths.append("amount_micros")
        client.get_service("CampaignBudgetService").mutate_campaign_budgets(
            customer_id=cid, operations=[op])
        print(f"✓ Budget: €{b.amount_micros/1e6:.0f} → €{NEW_BUDGET_MICROS/1e6:.0f}/day")

    # 2. Pause English campaign
    en_rn, en_status = campaign_rn(client, cid, EN_CAMPAIGN)
    if en_status == "PAUSED":
        print("• English campaign already PAUSED")
    elif en_rn:
        op = client.get_type("CampaignOperation")
        op.update.resource_name = en_rn
        op.update.status = client.enums.CampaignStatusEnum.PAUSED
        op.update_mask.paths.append("status")
        client.get_service("CampaignService").mutate_campaigns(customer_id=cid, operations=[op])
        print(f"✓ Paused campaign: {EN_CAMPAIGN}")

    # 3. Pause "pintores madrid" keyword
    rows = search(client, cid, """
        SELECT ad_group_criterion.resource_name, ad_group_criterion.status
        FROM ad_group_criterion
        WHERE ad_group_criterion.type = 'KEYWORD'
          AND ad_group_criterion.keyword.text = 'pintores madrid'
          AND ad_group_criterion.keyword.match_type = 'PHRASE'
          AND ad_group.name = 'Pintar Piso Madrid'
          AND ad_group_criterion.status != 'REMOVED'""")
    for r in rows:
        if r.ad_group_criterion.status.name == "PAUSED":
            print("• Keyword 'pintores madrid' already PAUSED")
            continue
        op = client.get_type("AdGroupCriterionOperation")
        op.update.resource_name = r.ad_group_criterion.resource_name
        op.update.status = client.enums.AdGroupCriterionStatusEnum.PAUSED
        op.update_mask.paths.append("status")
        client.get_service("AdGroupCriterionService").mutate_ad_group_criteria(
            customer_id=cid, operations=[op])
        print("✓ Paused keyword: pintores madrid (PHRASE)")

    # 4. Negatives
    rows = search(client, cid,
                  "SELECT shared_set.resource_name FROM shared_set "
                  f"WHERE shared_set.name = '{NEGATIVE_LIST_NAME}' AND shared_set.status = 'ENABLED'")
    ss_rn = rows[0].shared_set.resource_name
    existing = {r.shared_criterion.keyword.text.lower() for r in search(
        client, cid,
        f"SELECT shared_criterion.keyword.text FROM shared_criterion "
        f"WHERE shared_criterion.shared_set = '{ss_rn}'")}
    ops = []
    for text, match in NEW_NEGATIVES:
        if text.lower() in existing:
            print(f"• Negative exists: {text}")
            continue
        op = client.get_type("SharedCriterionOperation")
        crit = op.create
        crit.shared_set = ss_rn
        crit.keyword.text = text
        crit.keyword.match_type = getattr(client.enums.KeywordMatchTypeEnum, match)
        ops.append(op)
        print(f"✓ Adding negative: {text} ({match})")
    if ops:
        client.get_service("SharedCriterionService").mutate_shared_criteria(
            customer_id=cid, operations=ops)

    # 5. Geo: Boadilla del Monte + Tres Cantos
    have = {r.campaign_criterion.location.geo_target_constant for r in search(
        client, cid,
        "SELECT campaign_criterion.location.geo_target_constant FROM campaign_criterion "
        f"WHERE campaign_criterion.type = 'LOCATION' AND campaign.resource_name = '{es_rn}'")}
    geo_rns = resolve_geo_targets(client, NEW_GEO_NAMES)
    ops = []
    for rn in geo_rns:
        if rn in have:
            print(f"• Geo target already attached: {rn}")
            continue
        op = client.get_type("CampaignCriterionOperation")
        crit = op.create
        crit.campaign = es_rn
        crit.location.geo_target_constant = rn
        ops.append(op)
    if ops:
        client.get_service("CampaignCriterionService").mutate_campaign_criteria(
            customer_id=cid, operations=ops)
        print(f"✓ {len(ops)} geo targets added")

    # 6. Zona keywords
    rows = search(client, cid,
                  "SELECT ad_group.resource_name FROM ad_group "
                  "WHERE ad_group.name = 'Pintores por Zona' AND ad_group.status != 'REMOVED'")
    zona_rn = rows[0].ad_group.resource_name
    live = {(r.ad_group_criterion.keyword.text.lower(), r.ad_group_criterion.keyword.match_type.name)
            for r in search(client, cid,
                            "SELECT ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type "
                            "FROM ad_group_criterion WHERE ad_group_criterion.type = 'KEYWORD' "
                            f"AND ad_group_criterion.status != 'REMOVED' AND ad_group.resource_name = '{zona_rn}'")}
    ops = []
    for text, match in NEW_ZONA_KEYWORDS:
        if (text, match) in live:
            print(f"• Zona keyword exists: {text}")
            continue
        op = client.get_type("AdGroupCriterionOperation")
        crit = op.create
        crit.ad_group = zona_rn
        crit.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        crit.keyword.text = text
        crit.keyword.match_type = getattr(client.enums.KeywordMatchTypeEnum, match)
        ops.append(op)
        print(f"✓ Adding zona keyword: {text} ({match})")
    if ops:
        client.get_service("AdGroupCriterionService").mutate_ad_group_criteria(
            customer_id=cid, operations=ops)

    print("\nDone.")


if __name__ == "__main__":
    main()
