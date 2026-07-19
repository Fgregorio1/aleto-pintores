"""Curates the Spanish campaign's keywords around high-intent, non-price-shopper searches.

2026-07-15 decision (Felipe): drop keywords that attract multi-quote price
comparison ("presupuesto ...", "... precio") and geo-less research terms, add
"hire a local pro" intent instead:
  - removes: "presupuesto pintar piso", "quitar gotele precio", "pintar piso" (EXACT)
  - adds to existing ad groups: empresa de pintura madrid, pintor madrid (EXACT),
    pintores cerca de mi, quitar gotele y pintar, alisado de paredes
  - creates ad group "Pintores por Zona" with one phrase keyword per geo-targeted
    town (demand proven by the search-terms report) + an ENABLED RSA
  - adds negatives: presupuesto, presupuestos, "lista de precios"

"precio"/"cuanto cuesta" queries are deliberately NOT negated yet — they can
still reach us via phrase close variants; cut them only if lead quality says so.

Idempotent: skips anything already present/absent. Keyword spec of record is
CAMPAIGNS in scripts/build_campaigns.py — keep both in sync.

Run: .venv/bin/python scripts/refine_keywords_intent.py
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

SITE = "https://aletopintores.com"
CAMPAIGN_NAME = "Aleto Pintores - Madrid (Spanish)"
NEGATIVE_LIST_NAME = "Aleto Universal Negatives"

REMOVE_KEYWORDS = [
    ("Pintar Piso Madrid", "presupuesto pintar piso", "PHRASE"),
    ("Pintar Piso Madrid", "pintar piso", "EXACT"),
    ("Quitar Gotelé Madrid", "quitar gotele precio", "PHRASE"),
]

ADD_KEYWORDS = {
    "Pintar Piso Madrid": [
        ("empresa de pintura madrid", "PHRASE"),
        ("pintor madrid", "EXACT"),
        ("pintores cerca de mi", "PHRASE"),
    ],
    "Quitar Gotelé Madrid": [
        ("quitar gotele y pintar", "PHRASE"),
        ("alisado de paredes", "PHRASE"),
    ],
}

# One phrase keyword per geo-targeted town (campaign geo = these 11 + Madrid).
# Short forms on purpose: "pintores pozuelo" also catches "pintores en pozuelo
# de alarcón" etc.
ZONA_AD_GROUP = {
    "name": "Pintores por Zona",
    "final_url": f"{SITE}/servicios/pintura-interior-pisos/",
    "path1": "pintores",
    "path2": "tu-zona",
    "keywords": [
        ("pintores alcobendas", "PHRASE"),
        ("pintores getafe", "PHRASE"),
        ("pintores leganes", "PHRASE"),
        ("pintores mostoles", "PHRASE"),
        ("pintores fuenlabrada", "PHRASE"),
        ("pintores alcorcon", "PHRASE"),
        ("pintores pozuelo", "PHRASE"),
        ("pintores las rozas", "PHRASE"),
        ("pintores majadahonda", "PHRASE"),
        ("pintores rivas", "PHRASE"),
        ("pintores san sebastian de los reyes", "PHRASE"),
    ],
    "headlines": [
        "Pintores en tu zona",
        "Pintores cerca de ti",
        "Precio cerrado en 24 h",
        "Piso de 80 m² desde 1.250 €",
        "Terminado en 4-5 días",
        "Fechas de entrega por escrito",
        "Sin sorpresas en la factura",
        "Muebles y suelos protegidos",
        "El mismo equipo cada día",
        "Repaso final pared a pared",
        "Seguro de RC de 300.000 €",
        "Pintura de primera marca",
        "Factura y garantía por escrito",
        "Visita gratis en tu casa",
        "Pintura interior y gotelé",
    ],
    "descriptions": [
        "Pintores profesionales en tu zona. Precio cerrado y por escrito antes de empezar.",
        "Protegemos el 100% de muebles y suelos y repasamos contigo pared a pared antes de cobrar.",
        "Piso de 80 m² desde 1.250 € con materiales incluidos, terminado en 4-5 días.",
        "Seguro de RC de 300.000 € con Mapfre, factura con IVA y garantía por escrito.",
    ],
}

NEW_NEGATIVES = [
    ("presupuesto", "BROAD"),
    ("presupuestos", "BROAD"),
    ("lista de precios", "PHRASE"),
]


def get_client():
    config = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
        "use_proto_plus": True,
    }
    return GoogleAdsClient.load_from_dict(config)


def search(client, customer_id, query):
    svc = client.get_service("GoogleAdsService")
    return list(svc.search(customer_id=customer_id, query=query))


def get_campaign_rn(client, customer_id):
    rows = search(
        client,
        customer_id,
        "SELECT campaign.resource_name FROM campaign "
        f"WHERE campaign.name = '{CAMPAIGN_NAME}'",
    )
    if not rows:
        print(f"✗ Campaign not found: {CAMPAIGN_NAME}")
        sys.exit(1)
    return rows[0].campaign.resource_name


def get_ad_group_rns(client, customer_id, campaign_rn):
    rows = search(
        client,
        customer_id,
        "SELECT ad_group.resource_name, ad_group.name FROM ad_group "
        f"WHERE ad_group.campaign = '{campaign_rn}' "
        "AND ad_group.status != 'REMOVED'",
    )
    return {r.ad_group.name: r.ad_group.resource_name for r in rows}


def get_keywords(client, customer_id, campaign_rn):
    """Returns {(ad_group_name, text, match_type): criterion_rn} for live keywords."""
    rows = search(
        client,
        customer_id,
        "SELECT ad_group.name, ad_group_criterion.resource_name, "
        "ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type "
        "FROM ad_group_criterion "
        "WHERE ad_group_criterion.type = 'KEYWORD' "
        "AND ad_group_criterion.negative = FALSE "
        "AND ad_group_criterion.status != 'REMOVED' "
        f"AND campaign.resource_name = '{campaign_rn}'",
    )
    return {
        (
            r.ad_group.name,
            r.ad_group_criterion.keyword.text.lower(),
            r.ad_group_criterion.keyword.match_type.name,
        ): r.ad_group_criterion.resource_name
        for r in rows
    }


def remove_keywords(client, customer_id, live_keywords):
    ops = []
    for ag_name, text, match in REMOVE_KEYWORDS:
        key = (ag_name, text.lower(), match)
        rn = live_keywords.get(key)
        if not rn:
            print(f"  • Already gone: [{ag_name}] {text} ({match})")
            continue
        op = client.get_type("AdGroupCriterionOperation")
        op.remove = rn
        ops.append(op)
        print(f"  ✓ Removing: [{ag_name}] {text} ({match})")
    if ops:
        svc = client.get_service("AdGroupCriterionService")
        svc.mutate_ad_group_criteria(customer_id=customer_id, operations=ops)
        print(f"  ✓ {len(ops)} keywords removed")


def add_keywords(client, customer_id, ad_group_rn, keywords, ag_name, live_keywords):
    match_enum = client.enums.KeywordMatchTypeEnum
    ops = []
    for text, match in keywords:
        if (ag_name, text.lower(), match) in live_keywords:
            print(f"  • Already present: [{ag_name}] {text} ({match})")
            continue
        op = client.get_type("AdGroupCriterionOperation")
        crit = op.create
        crit.ad_group = ad_group_rn
        crit.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        crit.keyword.text = text
        crit.keyword.match_type = getattr(match_enum, match)
        ops.append(op)
        print(f"  ✓ Adding: [{ag_name}] {text} ({match})")
    if ops:
        svc = client.get_service("AdGroupCriterionService")
        svc.mutate_ad_group_criteria(customer_id=customer_id, operations=ops)
        print(f"  ✓ {len(ops)} keywords added to {ag_name}")


def ensure_zona_ad_group(client, customer_id, campaign_rn, ad_group_rns, live_keywords):
    spec = ZONA_AD_GROUP
    ag_rn = ad_group_rns.get(spec["name"])
    created = False
    if ag_rn:
        print(f"  • Ad group exists: {spec['name']}")
    else:
        op = client.get_type("AdGroupOperation")
        ag = op.create
        ag.name = spec["name"]
        ag.campaign = campaign_rn
        ag.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
        ag.status = client.enums.AdGroupStatusEnum.ENABLED
        svc = client.get_service("AdGroupService")
        resp = svc.mutate_ad_groups(customer_id=customer_id, operations=[op])
        ag_rn = resp.results[0].resource_name
        created = True
        print(f"  ✓ Created ad group: {spec['name']}")

    add_keywords(client, customer_id, ag_rn, spec["keywords"], spec["name"], live_keywords)

    has_ad = search(
        client,
        customer_id,
        "SELECT ad_group_ad.resource_name FROM ad_group_ad "
        f"WHERE ad_group_ad.ad_group = '{ag_rn}' "
        "AND ad_group_ad.status != 'REMOVED'",
    )
    if has_ad:
        print(f"  • RSA already present in {spec['name']}")
        return
    op = client.get_type("AdGroupAdOperation")
    aga = op.create
    aga.ad_group = ag_rn
    aga.status = client.enums.AdGroupAdStatusEnum.ENABLED
    ad = aga.ad
    ad.final_urls.append(spec["final_url"])
    rsa = ad.responsive_search_ad
    for text in spec["headlines"]:
        asset = client.get_type("AdTextAsset")
        asset.text = text
        rsa.headlines.append(asset)
    for text in spec["descriptions"]:
        asset = client.get_type("AdTextAsset")
        asset.text = text
        rsa.descriptions.append(asset)
    rsa.path1 = spec["path1"]
    rsa.path2 = spec["path2"]
    svc = client.get_service("AdGroupAdService")
    svc.mutate_ad_group_ads(customer_id=customer_id, operations=[op])
    print(f"  ✓ RSA added (ENABLED): {len(spec['headlines'])} headlines, "
          f"{len(spec['descriptions'])} descriptions")


def add_negatives(client, customer_id):
    rows = search(
        client,
        customer_id,
        "SELECT shared_set.resource_name FROM shared_set "
        f"WHERE shared_set.name = '{NEGATIVE_LIST_NAME}' "
        "AND shared_set.status = 'ENABLED'",
    )
    if not rows:
        print(f"  ⚠ Shared set '{NEGATIVE_LIST_NAME}' not found — skipping negatives")
        return
    shared_set_rn = rows[0].shared_set.resource_name
    existing = {
        r.shared_criterion.keyword.text.lower()
        for r in search(
            client,
            customer_id,
            "SELECT shared_criterion.keyword.text FROM shared_criterion "
            f"WHERE shared_criterion.shared_set = '{shared_set_rn}'",
        )
    }
    match_enum = client.enums.KeywordMatchTypeEnum
    ops = []
    for text, match in NEW_NEGATIVES:
        if text.lower() in existing:
            print(f"  • Negative already present: {text}")
            continue
        op = client.get_type("SharedCriterionOperation")
        crit = op.create
        crit.shared_set = shared_set_rn
        crit.keyword.text = text
        crit.keyword.match_type = getattr(match_enum, match)
        ops.append(op)
        print(f"  ✓ Adding negative: {text} ({match})")
    if ops:
        svc = client.get_service("SharedCriterionService")
        svc.mutate_shared_criteria(customer_id=customer_id, operations=ops)
        print(f"  ✓ {len(ops)} negatives added")


def main():
    client = get_client()
    customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    campaign_rn = get_campaign_rn(client, customer_id)
    ad_group_rns = get_ad_group_rns(client, customer_id, campaign_rn)
    live_keywords = get_keywords(client, customer_id, campaign_rn)

    try:
        print("\n1. Removing price-shopper keywords…")
        remove_keywords(client, customer_id, live_keywords)

        print("\n2. Adding high-intent keywords to existing ad groups…")
        for ag_name, kws in ADD_KEYWORDS.items():
            rn = ad_group_rns.get(ag_name)
            if not rn:
                print(f"  ⚠ Ad group not found: {ag_name}")
                continue
            add_keywords(client, customer_id, rn, kws, ag_name, live_keywords)

        print("\n3. Ensuring 'Pintores por Zona' ad group…")
        ensure_zona_ad_group(
            client, customer_id, campaign_rn, ad_group_rns, live_keywords
        )

        print("\n4. Adding price-shopper negatives…")
        add_negatives(client, customer_id)
    except GoogleAdsException as ex:
        print(f"✗ Google Ads API error: {ex.error.code().name}")
        for error in ex.failure.errors:
            print(f"\t{error.message}")
        sys.exit(1)

    print("\nDone. Verify with: .venv/bin/python scripts/check_search_terms.py")


if __name__ == "__main__":
    main()
