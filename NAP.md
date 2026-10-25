# NAP — Canonical Business Record

**This is the single source of truth for Aleto Pintores' Name, Address, Phone (NAP).**
Copy it **verbatim** into every citation, directory, profile, schema block, and footer — forever.
Any inconsistency (abbreviations, missing suffix, different phone format) fragments the entity and weakens local + AI-search ranking. When something here changes, change it *here first*, then propagate everywhere and re-audit (see `docs/02` §8).

---

## Canonical block (copy-paste verbatim)

```
Aleto Pintores
Rafaela Ybarra Kalea, 14, Deusto, 48014 Bilbao, Bizkaia
+34 624 04 62 10
contacto@aletopintores.com
https://aletopintores.com
```

## Structured fields

| Field | Value |
|---|---|
| **Business name** | Aleto Pintores |
| **Street** | Rafaela Ybarra Kalea, 14 |
| **District (barrio)** | Deusto |
| **Postal code** | 48014 |
| **City** | Bilbao |
| **Region (province)** | Bizkaia (País Vasco) |
| **Service area** | Gran Bilbao — on-site line: "Atendemos todo el Gran Bilbao." |
| **Country** | España / Spain (ES) |
| **Phone (display)** | 624 04 62 10 |
| **Phone (E.164, for schema/`tel:`)** | +34624046210 |
| **Email** | contacto@aletopintores.com |
| **Website** | https://aletopintores.com |
| **Hours** | 24 h — abierto todos los días (24/7) |

## Format rules

- **Phone:** display as `624 04 62 10`; use `+34624046210` in `LocalBusiness` schema `telephone` and in `tel:` links. Always include `+34` on directories that accept international format.
- **Address:** write the street as `Rafaela Ybarra Kalea, 14` (not `Calle Rafaela Ybarra`/`C. de` variants) so every listing matches byte-for-byte. Keep `Deusto`, `48014 Bilbao` and `Bizkaia` in that order. (Moved from C. de Juan de Austria, 13, Chamberí, 28010 Madrid on 2026-10-25 — every old citation must be updated.)
- **Hours (schema):** 24/7 → `openingHours: "Mo-Su 00:00-23:59"` (or `openingHoursSpecification` with `opens 00:00 / closes 23:59` for all seven days). Present it on-site as "Atención 24 h".
- **Domain:** `aletopintores.com` is primary. (Note: `docs/02` originally recommended `.es` primary — decision reversed to `.com`. If `aletopintores.es` is also owned, 301-redirect it to `.com` and list only `.com` as the canonical URL.)

## Where this must appear identically

Site footer · GBP · Bing Places · Apple Business Connect · Habitissimo · Cronoshare · Houzz · Páginas Amarillas · QDQ · Yelp.es · Cylex · Infobel · `sameAs`/`LocalBusiness` schema · all social bios. Full checklist: `docs/02` §8.
