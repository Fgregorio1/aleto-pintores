"""Phase C of the 2026-07-19 CRO rebuild: remove every price figure from ads.

The site no longer shows prices (Wolf blueprint), so ads must stop promising
them: removes PRICE assets and the two price sitelinks from the Spanish
campaign, and replaces each ad group's RSA (RSAs are immutable) with
price-free copy. "Precio cerrado en 24 h" claims stay — a fixed-quote
promise, not a published price. Old RSAs are PAUSED, not removed (history).

Idempotent: skips work already done. Run:
.venv/bin/python scripts/ads_no_price_rewrite.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from build_campaigns import get_client, search

ES_CAMPAIGN = "Aleto Pintores - Madrid (Spanish)"
PRICE_SITELINKS = {"Precios de pintura 2026", "Guía: pintar un piso"}

COMMON_D = [
    "Protegemos el 100% de muebles y suelos y repasamos contigo pared a pared antes de cobrar.",
    "El mismo equipo del primer al último día, con seguro de RC y garantía por escrito.",
]

RSAS = {
    "Pintar Piso Madrid": {
        "path1": "pintar-piso", "path2": "madrid",
        "headlines": [
            "Pintores en Madrid", "Pintar tu piso en Madrid", "Presupuesto cerrado en 24 h",
            "Visita gratuita en tu casa", "Terminado en 4-5 días", "Fechas de entrega por escrito",
            "Sin sorpresas en la factura", "Muebles y suelos protegidos", "El mismo equipo cada día",
            "Repaso final pared a pared", "Seguro de RC de 300.000 €", "Pintura de primera marca",
            "Factura y garantía por escrito", "Limpieza cada tarde", "Oficio de 7 años en EE.UU.",
        ],
        "descriptions": [
            "Presupuesto cerrado y gratis en 24 h, con fecha de inicio y de entrega por escrito.",
            *COMMON_D,
            "Visita gratuita de 20 minutos y tu piso pintado en días, no en semanas.",
        ],
    },
    "Quitar Gotelé Madrid": {
        "path1": "quitar-gotele", "path2": "madrid",
        "headlines": [
            "Quitar gotelé en Madrid", "Alisar paredes en Madrid", "Paredes lisas de verdad",
            "Sin polvo por toda la casa", "Lijado con aspiración", "Sigue viviendo en tu casa",
            "Acabado revisado a contraluz", "Presupuesto cerrado en 24 h", "Diagnóstico gratis en tu casa",
            "Adiós al gotelé para siempre", "Terminado en 4-6 días", "Pintura incluida",
            "Precio cerrado, sin sorpresas", "Garantía por escrito", "Visita gratis, sin compromiso",
        ],
        "descriptions": [
            "Quitamos el gotelé y alisamos tus paredes con lijado conectado a aspiración: sin polvo.",
            "Sellado por estancias y limpieza diaria: tu casa sigue habitable toda la obra.",
            "Entrega estancia por estancia comprobada a contraluz. Factura y garantía por escrito.",
            "Visita gratuita y presupuesto cerrado en 24 h, con fechas firmadas antes de empezar.",
        ],
    },
    "Pintores por Zona": {
        "path1": "pintores", "path2": "tu-zona",
        "headlines": [
            "Pintores en tu zona", "Pintores cerca de ti", "Presupuesto cerrado en 24 h",
            "Visita gratis en tu casa", "Terminado en 4-5 días", "Fechas de entrega por escrito",
            "Sin sorpresas en la factura", "Muebles y suelos protegidos", "El mismo equipo cada día",
            "Repaso final pared a pared", "Seguro de RC de 300.000 €", "Pintura de primera marca",
            "Factura y garantía por escrito", "Pintura interior y gotelé", "Respuesta hoy mismo",
        ],
        "descriptions": [
            "Pintores profesionales en tu municipio. Precio cerrado y por escrito antes de empezar.",
            *COMMON_D,
            "Visita gratuita de 20 minutos y presupuesto cerrado en 24 horas. Sin compromiso.",
        ],
    },
}


def main():
    client = get_client()
    cid = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    rows = search(client, cid,
                  "SELECT campaign.resource_name FROM campaign "
                  f"WHERE campaign.name = '{ES_CAMPAIGN}'")
    camp_rn = rows[0].campaign.resource_name

    # 1. Remove PRICE assets from the campaign
    rows = search(client, cid, f"""
        SELECT campaign_asset.resource_name FROM campaign_asset
        WHERE campaign_asset.campaign = '{camp_rn}'
          AND campaign_asset.field_type = 'PRICE'
          AND campaign_asset.status != 'REMOVED'""")
    ops = []
    for r in rows:
        op = client.get_type("CampaignAssetOperation")
        op.remove = r.campaign_asset.resource_name
        ops.append(op)
    if ops:
        client.get_service("CampaignAssetService").mutate_campaign_assets(customer_id=cid, operations=ops)
        print(f"✓ {len(ops)} price asset link(s) removed")
    else:
        print("• No price assets attached")

    # 2. Remove price sitelinks
    rows = search(client, cid, f"""
        SELECT campaign_asset.resource_name, asset.sitelink_asset.link_text
        FROM campaign_asset
        WHERE campaign_asset.campaign = '{camp_rn}'
          AND campaign_asset.field_type = 'SITELINK'
          AND campaign_asset.status != 'REMOVED'""")
    ops = []
    for r in rows:
        if r.asset.sitelink_asset.link_text in PRICE_SITELINKS:
            op = client.get_type("CampaignAssetOperation")
            op.remove = r.campaign_asset.resource_name
            ops.append(op)
            print(f"✓ Removing sitelink: {r.asset.sitelink_asset.link_text}")
    if ops:
        client.get_service("CampaignAssetService").mutate_campaign_assets(customer_id=cid, operations=ops)
    else:
        print("• No price sitelinks attached")

    # 3. Replace RSAs per ad group
    for ag_name, spec in RSAS.items():
        rows = search(client, cid, f"""
            SELECT ad_group.resource_name, ad_group_ad.resource_name, ad_group_ad.status,
                   ad_group_ad.ad.final_urls, ad_group_ad.ad.responsive_search_ad.headlines
            FROM ad_group_ad
            WHERE ad_group.name = '{ag_name}'
              AND campaign.resource_name = '{camp_rn}'
              AND ad_group_ad.status = 'ENABLED'""")
        if not rows:
            print(f"⚠ No enabled RSA in {ag_name}")
            continue
        old = rows[0]
        old_heads = [h.text for h in old.ad_group_ad.ad.responsive_search_ad.headlines]
        if any("€" in h and "300.000" not in h for h in old_heads) is False:
            print(f"• {ag_name}: enabled RSA already price-free")
            continue
        final_urls = list(old.ad_group_ad.ad.final_urls)

        op = client.get_type("AdGroupAdOperation")
        aga = op.create
        aga.ad_group = old.ad_group.resource_name
        aga.status = client.enums.AdGroupAdStatusEnum.ENABLED
        ad = aga.ad
        for u in final_urls:
            ad.final_urls.append(u)
        rsa = ad.responsive_search_ad
        for text in spec["headlines"]:
            a = client.get_type("AdTextAsset"); a.text = text; rsa.headlines.append(a)
        for text in spec["descriptions"]:
            a = client.get_type("AdTextAsset"); a.text = text; rsa.descriptions.append(a)
        rsa.path1 = spec["path1"]; rsa.path2 = spec["path2"]
        client.get_service("AdGroupAdService").mutate_ad_group_ads(customer_id=cid, operations=[op])

        pause = client.get_type("AdGroupAdOperation")
        pause.update.resource_name = old.ad_group_ad.resource_name
        pause.update.status = client.enums.AdGroupAdStatusEnum.PAUSED
        pause.update_mask.paths.append("status")
        client.get_service("AdGroupAdService").mutate_ad_group_ads(customer_id=cid, operations=[pause])
        print(f"✓ {ag_name}: new price-free RSA enabled, old RSA paused")

    print("\nDone.")


if __name__ == "__main__":
    main()
