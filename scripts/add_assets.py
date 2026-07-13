"""Adds URL tracking suffix + call/callout/structured-snippet/price assets.

Reads URL_SUFFIX, CALL_ASSET, CALLOUTS, SNIPPETS and PRICE_ASSETS from
build_campaigns.py and applies them to both campaigns. Idempotent: existing
assets are found by their identifying text and reused; existing campaign
links and matching URL suffixes are skipped.

Run: .venv/bin/python scripts/add_assets.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from build_campaigns import (
    CALL_ASSET,
    CALLOUTS,
    PRICE_ASSETS,
    SNIPPETS,
    URL_SUFFIX,
    get_client,
    search,
)

MAX_TEXT = 25  # callout text, snippet values, price header/description


def validate():
    ok = True
    for campaign, texts in CALLOUTS.items():
        for t in texts:
            if len(t) > MAX_TEXT:
                print(f"✗ Callout >{MAX_TEXT} chars ({len(t)}): {t}")
                ok = False
    for campaign, snip in SNIPPETS.items():
        for v in snip["values"]:
            if len(v) > MAX_TEXT:
                print(f"✗ Snippet value >{MAX_TEXT} chars ({len(v)}): {v}")
                ok = False
        if not 3 <= len(snip["values"]) <= 10:
            print(f"✗ {campaign}: snippets need 3-10 values")
            ok = False
    for campaign, pa in PRICE_ASSETS.items():
        for o in pa["offerings"]:
            for key in ("header", "desc"):
                if len(o[key]) > MAX_TEXT:
                    print(f"✗ Price {key} >{MAX_TEXT} chars ({len(o[key])}): {o[key]}")
                    ok = False
        if not 3 <= len(pa["offerings"]) <= 8:
            print(f"✗ {campaign}: price assets need 3-8 offerings")
            ok = False
    if not ok:
        sys.exit(1)
    print("✓ All asset copy within limits")


def campaign_rn_by_name(client, customer_id, name):
    rows = search(
        client,
        customer_id,
        "SELECT campaign.resource_name, campaign.final_url_suffix FROM campaign "
        f"WHERE campaign.name = '{name}' AND campaign.status != 'REMOVED'",
    )
    return rows[0] if rows else None


def set_url_suffix(client, customer_id, row, suffix):
    campaign = row.campaign
    if campaign.final_url_suffix == suffix:
        print("  • final_url_suffix already set")
        return
    op = client.get_type("CampaignOperation")
    op.update.resource_name = campaign.resource_name
    op.update.final_url_suffix = suffix
    op.update_mask.paths.append("final_url_suffix")
    svc = client.get_service("CampaignService")
    svc.mutate_campaigns(customer_id=customer_id, operations=[op])
    print("  ✓ final_url_suffix set (UTM + ValueTrack params)")


def create_asset(client, customer_id, op):
    svc = client.get_service("AssetService")
    resp = svc.mutate_assets(customer_id=customer_id, operations=[op])
    return resp.results[0].resource_name


def ensure_call_conversion_action(client, customer_id):
    """Call assets need an AD_CALL-type conversion action; create if missing."""
    rows = search(
        client,
        customer_id,
        "SELECT conversion_action.resource_name, conversion_action.name "
        "FROM conversion_action WHERE conversion_action.type = 'AD_CALL' "
        "AND conversion_action.status = 'ENABLED'",
    )
    if rows:
        print(f"✓ AD_CALL conversion action exists: {rows[0].conversion_action.name}")
        return rows[0].conversion_action.resource_name
    op = client.get_type("ConversionActionOperation")
    ca = op.create
    ca.name = CALL_ASSET["conversion_name"]
    ca.type_ = client.enums.ConversionActionTypeEnum.AD_CALL
    ca.category = client.enums.ConversionActionCategoryEnum.PHONE_CALL_LEAD
    ca.status = client.enums.ConversionActionStatusEnum.ENABLED
    ca.phone_call_duration_seconds = CALL_ASSET["min_call_seconds"]
    ca.counting_type = (
        client.enums.ConversionActionCountingTypeEnum.ONE_PER_CLICK
    )
    svc = client.get_service("ConversionActionService")
    resp = svc.mutate_conversion_actions(customer_id=customer_id, operations=[op])
    print(f"✓ Created AD_CALL conversion action: {CALL_ASSET['conversion_name']}")
    return resp.results[0].resource_name


def ensure_call_asset(client, customer_id):
    rows = search(
        client,
        customer_id,
        "SELECT asset.resource_name FROM asset WHERE asset.type = 'CALL' "
        f"AND asset.call_asset.phone_number = '{CALL_ASSET['phone']}'",
    )
    if rows:
        return rows[0].asset.resource_name, False
    conversion_rn = ensure_call_conversion_action(client, customer_id)
    op = client.get_type("AssetOperation")
    call = op.create.call_asset
    call.country_code = CALL_ASSET["country"]
    call.phone_number = CALL_ASSET["phone"]
    call.call_conversion_action = conversion_rn
    call.call_conversion_reporting_state = (
        client.enums.CallConversionReportingStateEnum.USE_RESOURCE_LEVEL_CALL_CONVERSION_ACTION
    )
    return create_asset(client, customer_id, op), True


def ensure_callout(client, customer_id, text):
    escaped = text.replace("'", "\\'")
    rows = search(
        client,
        customer_id,
        "SELECT asset.resource_name FROM asset WHERE asset.type = 'CALLOUT' "
        f"AND asset.callout_asset.callout_text = '{escaped}'",
    )
    if rows:
        return rows[0].asset.resource_name, False
    op = client.get_type("AssetOperation")
    op.create.callout_asset.callout_text = text
    return create_asset(client, customer_id, op), True


def ensure_snippet(client, customer_id, snip):
    rows = search(
        client,
        customer_id,
        "SELECT asset.resource_name, asset.structured_snippet_asset.header, "
        "asset.structured_snippet_asset.values FROM asset "
        "WHERE asset.type = 'STRUCTURED_SNIPPET' "
        f"AND asset.structured_snippet_asset.header = '{snip['header']}'",
    )
    for r in rows:
        if list(r.asset.structured_snippet_asset.values) == snip["values"]:
            return r.asset.resource_name, False
    op = client.get_type("AssetOperation")
    ss = op.create.structured_snippet_asset
    ss.header = snip["header"]
    ss.values.extend(snip["values"])
    return create_asset(client, customer_id, op), True


def ensure_price_asset(client, customer_id, pa):
    rows = search(
        client,
        customer_id,
        "SELECT asset.resource_name, asset.price_asset.language_code FROM asset "
        "WHERE asset.type = 'PRICE'",
    )
    for r in rows:
        if r.asset.price_asset.language_code == pa["language"]:
            return r.asset.resource_name, False
    op = client.get_type("AssetOperation")
    price = op.create.price_asset
    price.type_ = client.enums.PriceExtensionTypeEnum.SERVICES
    price.price_qualifier = client.enums.PriceExtensionPriceQualifierEnum.FROM
    price.language_code = pa["language"]
    for o in pa["offerings"]:
        offering = client.get_type("PriceOffering")
        offering.header = o["header"]
        offering.description = o["desc"]
        offering.price.currency_code = "EUR"
        offering.price.amount_micros = o["eur"] * 1_000_000
        offering.unit = client.enums.PriceExtensionPriceUnitEnum.UNSPECIFIED
        offering.final_url = o["url"]
        price.price_offerings.append(offering)
    return create_asset(client, customer_id, op), True


def link_assets(client, customer_id, campaign_rn, links):
    """links: list of (asset_rn, field_type_name, label)."""
    existing = {
        (r.campaign_asset.asset, r.campaign_asset.field_type.name)
        for r in search(
            client,
            customer_id,
            "SELECT campaign_asset.asset, campaign_asset.field_type "
            "FROM campaign_asset "
            f"WHERE campaign_asset.campaign = '{campaign_rn}' "
            "AND campaign_asset.status != 'REMOVED'",
        )
    }
    ops = []
    for asset_rn, field_type, label in links:
        if (asset_rn, field_type) in existing:
            print(f"  • already linked: {label}")
            continue
        op = client.get_type("CampaignAssetOperation")
        ca = op.create
        ca.campaign = campaign_rn
        ca.asset = asset_rn
        ca.field_type = getattr(client.enums.AssetFieldTypeEnum, field_type)
        ops.append(op)
        print(f"  ✓ linking: {label}")
    if ops:
        svc = client.get_service("CampaignAssetService")
        svc.mutate_campaign_assets(customer_id=customer_id, operations=ops)


def main():
    validate()
    client = get_client()
    customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")

    call_rn, created = ensure_call_asset(client, customer_id)
    print(f"✓ Call asset {'created' if created else 'exists'}: {CALL_ASSET['phone']}")

    for campaign_name in URL_SUFFIX:
        row = campaign_rn_by_name(client, customer_id, campaign_name)
        if not row:
            print(f"⚠ Campaign not found, skipping: {campaign_name}")
            continue
        campaign_rn = row.campaign.resource_name
        print(f"\n=== {campaign_name} ===")

        set_url_suffix(client, customer_id, row, URL_SUFFIX[campaign_name])

        links = [(call_rn, "CALL", f"call {CALL_ASSET['phone']}")]
        for text in CALLOUTS[campaign_name]:
            rn, created = ensure_callout(client, customer_id, text)
            links.append((rn, "CALLOUT", f"callout: {text}"))
        snip_rn, created = ensure_snippet(client, customer_id, SNIPPETS[campaign_name])
        links.append((snip_rn, "STRUCTURED_SNIPPET", f"snippet: {SNIPPETS[campaign_name]['header']}"))
        price_rn, created = ensure_price_asset(client, customer_id, PRICE_ASSETS[campaign_name])
        links.append((price_rn, "PRICE", f"price asset ({PRICE_ASSETS[campaign_name]['language']})"))

        link_assets(client, customer_id, campaign_rn, links)

    print("\nDone. Campaigns remain PAUSED.")


if __name__ == "__main__":
    main()
