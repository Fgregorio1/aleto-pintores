"""Builds the two launch Search campaigns for Aleto Pintores (all PAUSED).

Per docs/google-ads/googleads-prompt.md steps 1-3:
  1. "Aleto Pintores - Madrid (Spanish)"  — ad groups: Pintar Piso Madrid, Quitar Gotelé Madrid
  2. "Aleto Pintores - Expat Madrid (English)" — ad group: Expat Painters Madrid
Each campaign: Search only, 15 €/day, Maximize Clicks with 3 € CPC ceiling,
geo = Madrid + metro belt (src/data/business.ts areaServed), PAUSED until approval.
Attaches the "Aleto Universal Negatives" shared list to both campaigns
(run scripts/create_negative_list.py first if the list doesn't exist).

Idempotent: skips any campaign/ad group/list-attachment that already exists by name.

Run: .venv/bin/python scripts/build_campaigns.py
Reads creds from .env at the repo root.
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
DAILY_BUDGET_MICROS = 15_000_000  # 15 €/day
CPC_CEILING_MICROS = 3_000_000  # 3 € max CPC while on Maximize Clicks
NEGATIVE_LIST_NAME = "Aleto Universal Negatives"

# src/data/business.ts areaServed
GEO_NAMES = [
    "Madrid",
    "Alcorcón",
    "Móstoles",
    "Getafe",
    "Leganés",
    "Fuenlabrada",
    "Las Rozas de Madrid",
    "Pozuelo de Alarcón",
    "Majadahonda",
    "Alcobendas",
    "San Sebastián de los Reyes",
    "Rivas-Vaciamadrid",
]

LANG_ES = "languageConstants/1003"
LANG_EN = "languageConstants/1000"

CAMPAIGNS = [
    {
        "name": "Aleto Pintores - Madrid (Spanish)",
        "language": LANG_ES,
        # People physically in the service area.
        "geo_type": "PRESENCE",
        "ad_groups": [
            {
                "name": "Pintar Piso Madrid",
                "final_url": f"{SITE}/servicios/pintura-interior-pisos/",
                "path1": "pintar-piso",
                "path2": "madrid",
                "keywords": [
                    ("pintores madrid", "PHRASE"),
                    ("pintores en madrid", "PHRASE"),
                    ("empresa de pintores madrid", "PHRASE"),
                    ("pintar piso madrid", "PHRASE"),
                    ("pintar piso", "EXACT"),
                    ("presupuesto pintar piso", "PHRASE"),
                    ("pintar casa madrid", "PHRASE"),
                    ("pintores de interiores madrid", "PHRASE"),
                ],
                "headlines": [
                    "Pintores en Madrid",
                    "Pintar tu piso en Madrid",
                    "Presupuesto cerrado en 24 h",
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
                    "Visita y presupuesto gratis",
                    "¿Cuánto cuesta pintar tu piso?",
                ],
                "descriptions": [
                    "Presupuesto cerrado y gratis en 24 h, con fecha de inicio y de entrega por escrito.",
                    "Protegemos el 100% de muebles y suelos y repasamos contigo pared a pared antes de cobrar.",
                    "Piso de 80 m² desde 1.250 € con materiales incluidos, terminado en 4-5 días.",
                    "Seguro de RC de 300.000 € con Mapfre, factura con IVA y garantía por escrito.",
                ],
            },
            {
                "name": "Quitar Gotelé Madrid",
                "final_url": f"{SITE}/servicios/quitar-gotele-alisar-paredes/",
                "path1": "quitar-gotele",
                "path2": "madrid",
                "keywords": [
                    ("quitar gotele madrid", "PHRASE"),
                    ("quitar gotele", "EXACT"),
                    ("quitar gotele precio", "PHRASE"),
                    ("alisar paredes madrid", "PHRASE"),
                    ("alisar paredes", "EXACT"),
                    ("eliminar gotele madrid", "PHRASE"),
                    ("quitar gotele piso", "PHRASE"),
                ],
                "headlines": [
                    "Quitar gotelé en Madrid",
                    "Alisar paredes en Madrid",
                    "Desde 9 €/m² pintura incluida",
                    "Piso de 80 m²: 1.800-2.600 €",
                    "Terminado en 4-6 días",
                    "Sin polvo por toda la casa",
                    "Lijado con aspiración",
                    "Sigue viviendo en tu casa",
                    "Acabado revisado a contraluz",
                    "Presupuesto cerrado en 24 h",
                    "Diagnóstico gratis en tu casa",
                    "Adiós al gotelé para siempre",
                    "Paredes lisas de verdad",
                    "Precio cerrado, sin sorpresas",
                    "Visita y presupuesto gratis",
                ],
                "descriptions": [
                    "Quitamos el gotelé y alisamos tus paredes: 9-15 €/m² con pintura final incluida.",
                    "Sellado por estancias y lijado con aspiración industrial: sin polvo por toda la casa.",
                    "Piso de 80 m² entre 1.800 € y 2.600 €, terminado en 4-6 días. Presupuesto en 24 h.",
                    "Entrega estancia por estancia comprobada a contraluz. Factura y garantía por escrito.",
                ],
            },
        ],
    },
    {
        "name": "Aleto Pintores - Expat Madrid (English)",
        "language": LANG_EN,
        # Also reach landlords abroad searching for painters in Madrid.
        "geo_type": "PRESENCE_OR_INTEREST",
        "ad_groups": [
            {
                "name": "Expat Painters Madrid",
                "final_url": f"{SITE}/en/services/interior-painting-madrid/",
                "path1": "painters",
                "path2": "madrid",
                "keywords": [
                    ("painters madrid", "PHRASE"),
                    ("painters in madrid", "PHRASE"),
                    ("english speaking painters madrid", "PHRASE"),
                    ("painter madrid", "EXACT"),
                    ("painting company madrid", "PHRASE"),
                    ("house painters madrid", "PHRASE"),
                    ("apartment painting madrid", "PHRASE"),
                ],
                "headlines": [
                    "English Speaking Painters",
                    "Painters in Madrid",
                    "Fixed Quote in 24 Hours",
                    "80 m² Flat: €1,250–1,950",
                    "Painted in 4-5 Days",
                    "Everything in English",
                    "Dates & Price in Writing",
                    "No Surprises on the Bill",
                    "Furniture Fully Protected",
                    "Ideal for Landlords Abroad",
                    "Daily WhatsApp Photo Updates",
                    "Liability Insured (Mapfre)",
                    "VAT Invoice & Guarantee",
                    "Same Crew Start to Finish",
                    "Book Your Free Visit Today",
                ],
                "descriptions": [
                    "English-speaking painters in Madrid. Fixed written quote in 24 h — no surprises.",
                    "Quote, contract and WhatsApp updates in English. Same crew start to finish.",
                    "An 80 m² flat costs €1,250–1,950, finished in 4-5 days, materials included.",
                    "Abroad? Daily photo updates, video walkthrough at handover and VAT invoice by email.",
                ],
            },
        ],
    },
]


# Campaign-level sitelink assets (link_text ≤25 chars, desc lines ≤35 chars,
# every URL verified live). Consumed by scripts/add_sitelinks.py.
SITELINKS = {
    "Aleto Pintores - Madrid (Spanish)": [
        {
            "text": "Precios de pintura 2026",
            "url": f"{SITE}/precios/",
            "d1": "Tarifas reales por m² y por piso",
            "d2": "Guías de precios sin sorpresas",
        },
        {
            "text": "Quitar gotelé",
            "url": f"{SITE}/servicios/quitar-gotele-alisar-paredes/",
            "d1": "Desde 9 €/m² pintura incluida",
            "d2": "Paredes lisas en 4-6 días",
        },
        {
            "text": "Lacado de puertas",
            "url": f"{SITE}/servicios/lacado-puertas-armarios/",
            "d1": "Puertas y armarios como nuevos",
            "d2": "Acabado liso tipo fábrica",
        },
        {
            "text": "Todos los servicios",
            "url": f"{SITE}/servicios/",
            "d1": "Interior, gotelé, lacado y más",
            "d2": "Un equipo para toda la casa",
        },
        {
            "text": "Guía: pintar un piso",
            "url": f"{SITE}/precios/precio-pintar-piso-madrid/",
            "d1": "Cuánto cuesta en 2026",
            "d2": "Precios por tamaño de piso",
        },
        {
            "text": "Pide tu presupuesto",
            "url": f"{SITE}/presupuesto-gratis/",
            "d1": "Visita gratis y sin compromiso",
            "d2": "Precio cerrado en 24 horas",
        },
    ],
    "Aleto Pintores - Expat Madrid (English)": [
        {
            "text": "Painting Prices 2026",
            "url": f"{SITE}/en/prices/",
            "d1": "Real rates per m² and per flat",
            "d2": "Transparent cost guides",
        },
        {
            "text": "All Painting Services",
            "url": f"{SITE}/en/services/",
            "d1": "Interior, lacquer, gotelé & more",
            "d2": "One crew for the whole flat",
        },
        {
            "text": "Gotelé Removal",
            "url": f"{SITE}/en/services/gotele-removal-wall-smoothing/",
            "d1": "Smooth walls from €9/m²",
            "d2": "Paint included, 4-6 days",
        },
        {
            "text": "About Aleto",
            "url": f"{SITE}/en/about/",
            "d1": "Madrid crew, English support",
            "d2": "Same crew start to finish",
        },
        {
            "text": "For Architects",
            "url": f"{SITE}/en/for-architects-and-designers/",
            "d1": "Trade partner for your projects",
            "d2": "Deadlines you can plan around",
        },
        {
            "text": "Get a Free Quote",
            "url": f"{SITE}/en/free-estimate/",
            "d1": "Fixed quote within 24 hours",
            "d2": "Free visit, no obligation",
        },
    ],
}


# Tracking URL suffix per campaign (ValueTrack fills {keyword}/{creative}/
# {campaignid} at click time; Attribution.astro captures all six UTM params
# into the lead payload). Consumed by scripts/add_assets.py.
URL_SUFFIX = {
    "Aleto Pintores - Madrid (Spanish)": (
        "utm_source=google&utm_medium=cpc&utm_campaign=search-madrid-es"
        "&utm_term={keyword}&utm_content={creative}&utm_id={campaignid}"
    ),
    "Aleto Pintores - Expat Madrid (English)": (
        "utm_source=google&utm_medium=cpc&utm_campaign=search-expat-en"
        "&utm_term={keyword}&utm_content={creative}&utm_id={campaignid}"
    ),
}

# Call asset (both campaigns). Phone from src/data/business.ts. Call assets
# require an AD_CALL-type conversion action (the account's "Clicks to call"
# is GOOGLE_HOSTED and not usable here) — add_assets.py creates it if missing.
CALL_ASSET = {
    "phone": "+34624046210",
    "country": "ES",
    "conversion_name": "Calls from ads (60s+)",
    "min_call_seconds": 60,
}

# Callout assets (≤25 chars each; every claim sourced from site content).
CALLOUTS = {
    "Aleto Pintores - Madrid (Spanish)": [
        "Presupuesto en 24 h",
        "Precio cerrado",
        "Garantía por escrito",
        "Factura con IVA",
        "Visita gratis",
        "Seguro de resp. civil",
    ],
    "Aleto Pintores - Expat Madrid (English)": [
        "Fixed Quote in 24h",
        "Written Warranty",
        "VAT Invoice",
        "Free On-Site Visit",
        "English Spoken",
        "Liability Insured",
    ],
}

# Structured snippet assets (header from Google's fixed list; values ≤25 chars).
SNIPPETS = {
    "Aleto Pintores - Madrid (Spanish)": {
        "header": "Servicios",
        "values": [
            "Pintura interior",
            "Quitar gotelé",
            "Lacado de puertas",
            "Quitar papel pintado",
            "Pintura de fachadas",
            "Oficinas y locales",
        ],
    },
    "Aleto Pintores - Expat Madrid (English)": {
        "header": "Services",
        "values": [
            "Interior Painting",
            "Gotelé Removal",
            "Door Lacquering",
            "Wallpaper Removal",
            "Facade Painting",
            "Office Painting",
        ],
    },
}

# Price assets (type SERVICES, qualifier FROM; prices from src/data/precios.yaml,
# header/description ≤25 chars, 3-8 offerings per asset).
PRICE_ASSETS = {
    "Aleto Pintores - Madrid (Spanish)": {
        "language": "es",
        "offerings": [
            {
                "header": "Pintar piso 80 m²",
                "desc": "Todo incluido, 4-5 días",
                "eur": 1250,
                "url": f"{SITE}/servicios/pintura-interior-pisos/",
            },
            {
                "header": "Quitar gotelé 80 m²",
                "desc": "Pintura incluida",
                "eur": 1800,
                "url": f"{SITE}/servicios/quitar-gotele-alisar-paredes/",
            },
            {
                "header": "Lacar puertas",
                "desc": "Por puerta, en tu casa",
                "eur": 80,
                "url": f"{SITE}/servicios/lacado-puertas-armarios/",
            },
            {
                "header": "Quitar papel pintado",
                "desc": "Desde 4 €/m² de pared",
                "eur": 160,
                "url": f"{SITE}/servicios/quitar-papel-pintado/",
            },
            {
                "header": "Impermeabilizar terraza",
                "desc": "Garantía de 10 años",
                "eur": 500,
                "url": f"{SITE}/servicios/impermeabilizacion-terrazas/",
            },
        ],
    },
    "Aleto Pintores - Expat Madrid (English)": {
        "language": "en",
        "offerings": [
            {
                "header": "Interior Painting 80 m²",
                "desc": "All included, 4-5 days",
                "eur": 1250,
                "url": f"{SITE}/en/services/interior-painting-madrid/",
            },
            {
                "header": "Gotelé Removal 80 m²",
                "desc": "Paint included",
                "eur": 1800,
                "url": f"{SITE}/en/services/gotele-removal-wall-smoothing/",
            },
            {
                "header": "Door Lacquering",
                "desc": "Per door, at your home",
                "eur": 80,
                "url": f"{SITE}/en/services/door-cabinet-lacquering/",
            },
            {
                "header": "Terrace Waterproofing",
                "desc": "10-year warranty",
                "eur": 500,
                "url": f"{SITE}/en/services/terrace-waterproofing/",
            },
        ],
    },
}


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


def resolve_geo_targets(client, names):
    """Resolves location names to geo target constant resource names.

    Picks, per requested name, the highest-reach City/Municipality suggestion
    canonically inside the Community of Madrid, Spain.
    """
    svc = client.get_service("GeoTargetConstantService")
    request = client.get_type("SuggestGeoTargetConstantsRequest")
    request.locale = "es"
    request.country_code = "ES"
    request.location_names.names.extend(names)
    response = svc.suggest_geo_target_constants(request)

    best = {}
    for s in response.geo_target_constant_suggestions:
        gtc = s.geo_target_constant
        if "Madrid" not in gtc.canonical_name or gtc.target_type not in (
            "City",
            "Municipality",
        ):
            continue
        key = s.search_term
        if key not in best or s.reach > best[key][0]:
            best[key] = (s.reach, gtc.resource_name, gtc.canonical_name)

    resolved = []
    for name in names:
        if name in best:
            _, rn, canonical = best[name]
            print(f"  geo: {name} -> {canonical} ({rn})")
            resolved.append(rn)
        else:
            print(f"  ⚠ geo: no City match for '{name}' — skipped")
    return resolved


def ensure_budget(client, customer_id, name):
    rows = search(
        client,
        customer_id,
        "SELECT campaign_budget.resource_name FROM campaign_budget "
        f"WHERE campaign_budget.name = '{name}'",
    )
    if rows:
        return rows[0].campaign_budget.resource_name
    op = client.get_type("CampaignBudgetOperation")
    budget = op.create
    budget.name = name
    budget.amount_micros = DAILY_BUDGET_MICROS
    budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
    budget.explicitly_shared = False
    svc = client.get_service("CampaignBudgetService")
    resp = svc.mutate_campaign_budgets(customer_id=customer_id, operations=[op])
    return resp.results[0].resource_name


def ensure_campaign(client, customer_id, spec, budget_rn):
    rows = search(
        client,
        customer_id,
        "SELECT campaign.resource_name, campaign.status FROM campaign "
        f"WHERE campaign.name = '{spec['name']}'",
    )
    if rows:
        print(f"• Campaign exists, skipping create: {spec['name']}")
        return rows[0].campaign.resource_name, False

    op = client.get_type("CampaignOperation")
    campaign = op.create
    campaign.name = spec["name"]
    campaign.status = client.enums.CampaignStatusEnum.PAUSED
    campaign.advertising_channel_type = (
        client.enums.AdvertisingChannelTypeEnum.SEARCH
    )
    campaign.campaign_budget = budget_rn
    # Maximize Clicks with a CPC ceiling — sane default with zero conversion
    # history; switch to Maximize Conversions once ~15-30 conversions/month.
    campaign.target_spend.cpc_bid_ceiling_micros = CPC_CEILING_MICROS
    campaign.network_settings.target_google_search = True
    campaign.network_settings.target_search_network = False
    campaign.network_settings.target_content_network = False
    campaign.network_settings.target_partner_search_network = False
    campaign.geo_target_type_setting.positive_geo_target_type = getattr(
        client.enums.PositiveGeoTargetTypeEnum, spec["geo_type"]
    )
    campaign.geo_target_type_setting.negative_geo_target_type = (
        client.enums.NegativeGeoTargetTypeEnum.PRESENCE
    )
    campaign.contains_eu_political_advertising = (
        client.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
    )
    svc = client.get_service("CampaignService")
    resp = svc.mutate_campaigns(customer_id=customer_id, operations=[op])
    rn = resp.results[0].resource_name
    print(f"✓ Created campaign (PAUSED): {spec['name']}")
    return rn, True


def add_campaign_criteria(client, customer_id, campaign_rn, spec, geo_rns):
    ops = []
    for geo_rn in geo_rns:
        op = client.get_type("CampaignCriterionOperation")
        crit = op.create
        crit.campaign = campaign_rn
        crit.location.geo_target_constant = geo_rn
        ops.append(op)
    lang_op = client.get_type("CampaignCriterionOperation")
    lang_crit = lang_op.create
    lang_crit.campaign = campaign_rn
    lang_crit.language.language_constant = spec["language"]
    ops.append(lang_op)
    svc = client.get_service("CampaignCriterionService")
    svc.mutate_campaign_criteria(customer_id=customer_id, operations=ops)
    print(f"  ✓ {len(geo_rns)} locations + language targeting set")


def ensure_ad_group(client, customer_id, campaign_rn, ag_spec):
    rows = search(
        client,
        customer_id,
        "SELECT ad_group.resource_name FROM ad_group "
        f"WHERE ad_group.name = '{ag_spec['name']}' "
        f"AND ad_group.campaign = '{campaign_rn}'",
    )
    if rows:
        print(f"  • Ad group exists, skipping: {ag_spec['name']}")
        return rows[0].ad_group.resource_name, False
    op = client.get_type("AdGroupOperation")
    ag = op.create
    ag.name = ag_spec["name"]
    ag.campaign = campaign_rn
    ag.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
    ag.status = client.enums.AdGroupStatusEnum.ENABLED
    svc = client.get_service("AdGroupService")
    resp = svc.mutate_ad_groups(customer_id=customer_id, operations=[op])
    print(f"  ✓ Created ad group: {ag_spec['name']}")
    return resp.results[0].resource_name, True


def add_keywords(client, customer_id, ad_group_rn, keywords):
    match_enum = client.enums.KeywordMatchTypeEnum
    ops = []
    for text, match in keywords:
        op = client.get_type("AdGroupCriterionOperation")
        crit = op.create
        crit.ad_group = ad_group_rn
        crit.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        crit.keyword.text = text
        crit.keyword.match_type = getattr(match_enum, match)
        ops.append(op)
    svc = client.get_service("AdGroupCriterionService")
    resp = svc.mutate_ad_group_criteria(customer_id=customer_id, operations=ops)
    print(f"    ✓ {len(resp.results)} keywords added")


def add_rsa(client, customer_id, ad_group_rn, ag_spec):
    op = client.get_type("AdGroupAdOperation")
    aga = op.create
    aga.ad_group = ad_group_rn
    aga.status = client.enums.AdGroupAdStatusEnum.PAUSED
    ad = aga.ad
    ad.final_urls.append(ag_spec["final_url"])
    rsa = ad.responsive_search_ad
    for text in ag_spec["headlines"]:
        asset = client.get_type("AdTextAsset")
        asset.text = text
        rsa.headlines.append(asset)
    for text in ag_spec["descriptions"]:
        asset = client.get_type("AdTextAsset")
        asset.text = text
        rsa.descriptions.append(asset)
    rsa.path1 = ag_spec["path1"]
    rsa.path2 = ag_spec["path2"]
    svc = client.get_service("AdGroupAdService")
    svc.mutate_ad_group_ads(customer_id=customer_id, operations=[op])
    print(f"    ✓ RSA added (PAUSED): {len(ag_spec['headlines'])} headlines, "
          f"{len(ag_spec['descriptions'])} descriptions")


def attach_negative_list(client, customer_id, campaign_rn, campaign_name):
    rows = search(
        client,
        customer_id,
        "SELECT shared_set.resource_name FROM shared_set "
        f"WHERE shared_set.name = '{NEGATIVE_LIST_NAME}' "
        "AND shared_set.status = 'ENABLED'",
    )
    if not rows:
        print(f"  ⚠ Shared set '{NEGATIVE_LIST_NAME}' not found — "
              "run scripts/create_negative_list.py first")
        return
    shared_set_rn = rows[0].shared_set.resource_name
    existing = search(
        client,
        customer_id,
        "SELECT campaign_shared_set.resource_name FROM campaign_shared_set "
        f"WHERE campaign_shared_set.campaign = '{campaign_rn}' "
        f"AND campaign_shared_set.shared_set = '{shared_set_rn}'",
    )
    if existing:
        print(f"  • Negative list already attached to {campaign_name}")
        return
    op = client.get_type("CampaignSharedSetOperation")
    css = op.create
    css.campaign = campaign_rn
    css.shared_set = shared_set_rn
    svc = client.get_service("CampaignSharedSetService")
    svc.mutate_campaign_shared_sets(customer_id=customer_id, operations=[op])
    print(f"  ✓ Negative list attached to {campaign_name}")


def check_auto_tagging(client, customer_id):
    rows = search(
        client,
        customer_id,
        "SELECT customer.auto_tagging_enabled FROM customer",
    )
    enabled = rows[0].customer.auto_tagging_enabled
    if enabled:
        print("✓ Auto-tagging is enabled (gclid will be appended to ad clicks)")
        return
    print("⚠ Auto-tagging is DISABLED — enabling it (required for gclid "
          "capture and offline conversion uploads)…")
    op = client.get_type("CustomerOperation")
    op.update.resource_name = f"customers/{customer_id}"
    op.update.auto_tagging_enabled = True
    op.update_mask.paths.append("auto_tagging_enabled")
    svc = client.get_service("CustomerService")
    svc.mutate_customer(customer_id=customer_id, operation=op)
    print("✓ Auto-tagging enabled")


def main():
    client = get_client()
    customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")

    check_auto_tagging(client, customer_id)

    print("Resolving geo targets…")
    geo_rns = resolve_geo_targets(client, GEO_NAMES)
    if not geo_rns:
        print("✗ No geo targets resolved — aborting")
        sys.exit(1)

    for spec in CAMPAIGNS:
        print(f"\n=== {spec['name']} ===")
        budget_rn = ensure_budget(client, customer_id, f"Budget - {spec['name']}")
        campaign_rn, created = ensure_campaign(client, customer_id, spec, budget_rn)
        if created:
            add_campaign_criteria(client, customer_id, campaign_rn, spec, geo_rns)
        for ag_spec in spec["ad_groups"]:
            ag_rn, ag_created = ensure_ad_group(
                client, customer_id, campaign_rn, ag_spec
            )
            if ag_created:
                add_keywords(client, customer_id, ag_rn, ag_spec["keywords"])
                add_rsa(client, customer_id, ag_rn, ag_spec)
        attach_negative_list(client, customer_id, campaign_rn, spec["name"])

    print("\nDone. Both campaigns are PAUSED — review in the Google Ads UI "
          "and enable when ready.")


if __name__ == "__main__":
    main()
