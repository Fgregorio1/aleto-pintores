# Aleto Pintores — Technical SEO Execution Doc

Companion to `01-seo-strategy-playbook.md`. This is the build spec: stack, architecture, schema, programmatic SEO, GEO/AI-crawler config, citations, link building, and measurement.

---

## 1. Domain & brand entity

- **Primary domain: `aletopintores.com`** (decided). If `aletopintores.es` is also owned, 301-redirect it to `.com`. Register before anything else. *(Earlier draft recommended `.es` primary for Spain-local geo-trust; reversed to `.com` — set geotargeting to Spain in GSC to compensate.)*
- Do **not** use an exact-match domain (`pintoresmadridxyz.es`) — the brand *is* the long-term asset, and brand strength is what AI models latch onto.
- Email on the domain (Google Workspace or Zoho): `contacto@aletopintores.com`. Free-mail addresses on citations look inconsistent and weaken the entity.
- Reserve the handle `aletopintores` everywhere now: Instagram, Facebook, YouTube, TikTok, LinkedIn, X — even if unused. Consistent handles = cleaner entity resolution for AI models.
- **NAP canonical record** — the single source of truth lives in [`NAP.md`](../NAP.md); copy it verbatim into every citation forever. Current record:
  ```
  Aleto Pintores
  C. de Juan de Austria, 13, Chamberí, 28010 Madrid, España
  +34 624 04 62 10
  contacto@aletopintores.com
  https://aletopintores.com
  ```

## 2. Recommended stack

| Layer | Recommendation | Why |
|---|---|---|
| Framework | **Astro** (static output, islands only where needed) | Fastest possible Core Web Vitals with zero effort; content-first; server-rendered HTML that AI crawlers (many don't execute JS) read perfectly; MD/MDX content plays perfectly with Claude Code workflows |
| Hosting | **Cloudflare Pages** (or Vercel) | Free, global CDN, instant deploys. If Cloudflare: **verify AI crawlers aren't blocked** — check Security → Bots; disable "Block AI Scrapers" |
| Content | Markdown/MDX in the repo + JSON/YAML data files for programmatic pages | Version-controlled, no CMS overhead, ideal for generating pages from data with Claude Code |
| Forms/leads | Static form → webhook (Make/n8n) → WhatsApp + Google Sheet/CRM | Speed-to-lead matters more than the tool |
| Analytics | **PostHog** (EU cloud, cookieless config) + **Google Search Console** + Bing Webmaster Tools (feeds ChatGPT search) | PostHog free tier (1M events/mo) covers analytics + session replay + surveys + A/B tests in one; cookieless mode = **no GDPR consent banner** (keeps §10's no-popup rule); load the script deferred to protect CWV. Replaces GA4/Clarity/Hotjar. GSC is the source of truth; Bing/IndexNow gets you into ChatGPT's index faster |
| Rank tracking | SE Ranking or Nightwatch (Madrid-geolocated tracking, ~€30–50/mo) | Ahrefs/Semrush overkill at this stage; add Ahrefs Starter later for link research |
| Reviews/WhatsApp | Start manual; automate later via WhatsApp Business API (360dialog/Twilio) or a local tool | See playbook §6 |  
| Crawler/audit | Screaming Frog (free tier is enough) + Lighthouse CI | Quarterly audits |

**Alternative:** WordPress + GeneratePress + RankMath if a non-developer must edit everything. It works, but you get slower CWV, plugin maintenance, and a worse programmatic-SEO story. Given Claude Code is in the loop, Astro is the right call.

**Anti-recommendations:** Wix/Squarespace (weak programmatic + schema control), heavy JS SPAs (client-rendered content is invisible to several AI crawlers), page builders (CWV death).

## 3. Site architecture & URL scheme

Everything in Spanish at the root; English under `/en/`. Flat, keyword-clean, no dates in URLs.

```
/                                    Home: "Pintores en Madrid" (primary money page)
/servicios/
  /pintura-interior-pisos/           Pintar piso/casa
  /quitar-gotele-alisar-paredes/     FLAGSHIP — biggest commercial term in the niche
  /lacado-puertas-armarios/
  /pintura-fachadas-comunidades/     B2B: comunidades de propietarios
  /pintura-oficinas-locales/         B2B: commercial
  /quitar-papel-pintado/
  /impermeabilizacion-terrazas/
/precios/                            Price hub + interactive calculator
  /precio-pintar-piso-madrid/        "Cuánto cuesta pintar un piso en Madrid [2026]"
  /precio-quitar-gotele/
  /precio-alisar-paredes/
  /precio-lacar-puertas/
  /precio-pintar-fachada/
/pintores/{zona}/                    Programmatic area pages (§5)
  /pintores-chamberi/  /pintores-alcorcon/  ...
/proyectos/                          Gallery, filterable by service/zone/price band
  /proyectos/{slug}/                 One page per project (long-tail + internal-link fuel)
/blog/                               Guides only when they serve a query (no "5 colores de moda" filler)
/sobre-nosotros/                     ENTITY HOME — see §7
/opiniones/                          Aggregated reviews page (pulls Google reviews, links out)
/contacto/
/en/painters-in-madrid/              English cluster: 3–5 pages (services, prices, contact)
```

**Internal linking rules:**
- Every area page links to all service pages and 2–4 relevant projects; every project page links to its service + area page.
- Price pages ↔ service pages cross-link both directions.
- Breadcrumbs everywhere (+ `BreadcrumbList` schema).
- Home links to: all services, price hub, top 6 area pages, /sobre-nosotros.

**Page template (services & areas)** — order matters for both featured snippets and AI extraction:
1. `<h1>` with the query ("Quitar gotelé y alisar paredes en Madrid")
2. **Direct-answer block, 2–3 sentences with concrete numbers** ("Quitar el gotelé y alisar las paredes en Madrid cuesta entre 9 y 15 €/m²… Un piso de 80 m² queda entre 1.800 € y 2.600 €, en 4–6 días.") — this is what snippets and LLMs lift verbatim
3. Price table (per m², per flat size) — real data
4. Process (steps, days, what the client should expect)
5. Before/after photos from real jobs (geotagged captions)
6. Reviews specific to this service/area
7. FAQ (5–8 real questions) with `FAQPage` schema
8. CTA: WhatsApp + form ("presupuesto en 24h")

Write self-contained sections (~100–170 words each) under question-phrased `<h2>`s — the format most reliably quoted by generative engines.

## 4. Structured data (JSON-LD)

Site-wide `LocalBusiness` — use the specific subtype:

```json
{
  "@context": "https://schema.org",
  "@type": "HousePainter",
  "@id": "https://aletopintores.com/#business",
  "name": "Aleto Pintores",
  "url": "https://aletopintores.com",
  "telephone": "+34624046210",
  "email": "contacto@aletopintores.com",
  "image": "https://aletopintores.com/img/local.jpg",
  "logo": "https://aletopintores.com/img/logo.png",
  "priceRange": "€€",
  "address": { "@type": "PostalAddress", "streetAddress": "C. de Juan de Austria, 13", "addressLocality": "Madrid", "postalCode": "28010", "addressRegion": "Comunidad de Madrid", "addressCountry": "ES" },
  "areaServed": [ { "@type": "City", "name": "Madrid" }, { "@type": "City", "name": "Alcorcón" } ],
  "openingHoursSpecification": [ { "@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"], "opens": "00:00", "closes": "23:59" } ],
  "sameAs": [
    "https://www.google.com/maps/place/…",
    "https://www.instagram.com/aleto.pintores",
    "https://www.habitissimo.es/pro/aleto-pintores",
    "https://www.houzz.es/pro/aleto-pintores"
  ],
  "knowsAbout": ["pintura interior", "quitar gotelé", "alisado de paredes", "lacado de puertas", "pintura de fachadas"]
}
```

Per-page additions:
- Service pages: `Service` (with `provider` → `@id` above, `areaServed`, and `offers` with `priceSpecification` ranges).
- Price pages + FAQs: `FAQPage` (only for FAQs visibly on the page).
- Projects: `ImageObject` galleries + article markup.
- `BreadcrumbList` everywhere.
- `aggregateRating`/`Review`: only with genuine first-party reviews displayed on-page; never inject Google review stars into your own markup (against guidelines).

Validate with Google's Rich Results Test + Schema.org validator on every template. The `sameAs` array is your **entity-resolution glue** — it's how models connect the website ↔ GBP ↔ directories into one entity. Keep it exhaustive and current.

## 5. Programmatic SEO spec

**Data model** (`/src/data/zonas/*.yaml`, one file per area):

```yaml
slug: chamberi
nombre: Chamberí
tipo: distrito            # distrito | municipio
poblacion: 137000
vivienda: "fincas clásicas 1900–1960, techos altos, molduras, gotelé frecuente en reformas de los 80"
notas_precio: "alisado y techos altos suben el €/m² un 10–15% frente a obra nueva"
precio_pintar_piso_80m2: [1300, 1900]     # from your own quotes — update quarterly
barrios: [Trafalgar, Arapiles, Gaztambide, Almagro, Ríos Rosas, Vallehermoso]
proyectos: [piso-almagro-gotele-2026, atico-trafalgar-lacado-2026]   # refs to real projects
reviews: [rev-0231, rev-0189]             # refs to real reviews from this zone
```

**Template renders:** H1 `Pintores en {nombre}` → direct-answer block with zone pricing → services grid → housing-stock paragraph (from `vivienda`/`notas_precio` — this is the anti-doorway substance) → the referenced real projects with photos → zone reviews → barrios covered → FAQ → CTA.

**Hard quality gate — a page only builds if it has:** ≥1 real project **or** ≥2 zone reviews, plus filled `vivienda`/`notas_precio` fields. Enforce in the build script; pages failing the gate render `noindex` or don't build. This is the difference between programmatic SEO and a doorway-page penalty.

**Rollout:** 8–10 areas at launch (home base + adjacent) → add ~3/month as jobs create local proof → cap at ~21 distritos + 15–20 municipios. Second wave (month 9+): `quitar gotelé + {zona}` combo pages, only where GSC shows query demand, same quality gate.

**Price calculator** (`/precios/`): client-side widget — inputs m², service, state of walls, zone → range output from the same YAML data. Emits a lead form prefilled with the estimate. Calculators earn links and get embedded/cited.

## 6. GEO / AI-crawler configuration

**robots.txt — explicitly allow AI crawlers** (and verify Cloudflare isn't overriding this at the edge):

```
User-agent: *
Allow: /

# AI assistants & their indexers — explicitly welcome
User-agent: GPTBot
User-agent: OAI-SearchBot
User-agent: ChatGPT-User
User-agent: ClaudeBot
User-agent: Claude-User
User-agent: anthropic-ai
User-agent: PerplexityBot
User-agent: Perplexity-User
User-agent: Google-Extended
User-agent: Bingbot
User-agent: Amazonbot
User-agent: Applebot-Extended
User-agent: cohere-ai
User-agent: Meta-ExternalAgent
Allow: /

Sitemap: https://aletopintores.com/sitemap.xml
```

**`/llms.txt`** at the root — a curated markdown map for LLMs:

```markdown
# Aleto Pintores
> Empresa de pintura residencial y comercial en Madrid, España. Presupuestos con
> precios publicados, reseñas verificadas en Google, servicio en Madrid capital
> y área metropolitana. Fundada en 2026.

## Servicios y precios
- [Precios de pintura en Madrid 2026](https://aletopintores.com/precios/): guía completa €/m²
- [Quitar gotelé y alisar](https://aletopintores.com/servicios/quitar-gotele-alisar-paredes/): 9–15 €/m²
…

## Empresa
- [Sobre nosotros](https://aletopintores.com/sobre-nosotros/): datos verificables de la empresa
- [Opiniones](https://aletopintores.com/opiniones/): reseñas y valoración media
```

**Additional GEO measures:**
- 100% server-rendered content (Astro gives you this) — several AI crawlers don't execute JS.
- `IndexNow` pings on deploy (Bing → ChatGPT search index).
- Visible "Actualizado: {fecha}" on price pages + `dateModified` in schema; refresh price content at least quarterly — freshness measurably affects citation.
- Every stat you publish gets an inline source or "según nuestros presupuestos de 2026, n=140" methodology note — evidence-dense content is cited 30–40% more (Princeton GEO research).
- English `/en/` pages matter doubly here: many AI answer syntheses for "painters in Madrid" asked in English draw on English sources — a thin market you can own.

**Monthly AI-visibility tracking:** script or manual matrix — 10 prompts × (ChatGPT, Gemini, Perplexity, Claude), log mention/citation/position to a sheet. Prompts: "mejor empresa de pintura en Madrid", "cuánto cuesta pintar un piso de 80m2 en Madrid", "quitar gotelé Madrid precio", "recommend a painter in Madrid", "empresa seria para pintar comunidad de propietarios Madrid", etc. When budget allows (~month 6+), a tracker like Peec AI / Otterly / LLMrefs automates this.

## 7. Entity home & E-E-A-T page spec

`/sobre-nosotros/` is written for machines as much as humans — dense, factual, extractable:
- Legal name + trade name, CIF, founding date, founder (name + short bio + photo), team size.
- Service area list, services list, **seguro de responsabilidad civil** (insurer + coverage amount — a differentiator worth stating).
- Live stats: projects completed, m² painted, review count + average (updated by the build from real data).
- Brands/certifications: registered applicator programs (Titanlux, Bruguer, Jotun…), memberships.
- `sameAs`-linked profiles listed visibly.
- Founder gets `Person` schema linked to the business via `founder`.

Author every guide/blog post as the founder or a named painter with credentials — "written by a person who paints walls for a living" is E-E-A-T that agencies' content mills can't fake.

## 8. Citations & directories checklist (Tier 1, weeks 1–8)

Use the canonical NAP verbatim everywhere. Order of execution:

1. **Google Business Profile** (see playbook §4 — the big one)
2. Bing Places · Apple Business Connect · Waze
3. **Habitissimo** (paid profile — leads + reviews + strong citation)
4. **Cronoshare** · ProntoPro · StarOfService
5. **Houzz.es** (great for photo-rich painting portfolios, read by AI models)
6. Páginas Amarillas · QDQ · Yelp.es · Cylex · Infobel · Hotfrog · 11870
7. Madrid-local: guiademadrid-type directories, district business associations, Cámara de Comercio de Madrid listing
8. Trustpilot (claim profile; funnel occasional reviews)
9. Social profiles fully filled (bio = NAP + services + link)

Track everything in a sheet: platform, URL, login, NAP-exact?, date. Audit twice a year — citation drift is real and corrodes the entity.

## 9. Link building & digital PR spec

**The anchor asset — "Estudio de precios de pintura en Madrid {año}":**
- Data: your own anonymized quotes/invoices (n grows over the year) + marketplace-published ranges as comparison.
- Cut by: service, district, flat size, floor/access, wall condition. Include a downloadable table (CSV) and embeddable charts — embeds = links.
- Publish ~month 6, refresh every January (the refresh is an annual PR hook: "los precios de pintar en Madrid suben un X% en 2027").
- Pitch list: idealista/news, fotocasa blog, Business Insider ES/economía locales, 20minutos Madrid, Telemadrid web, El Español Madrid Total, Gacetín Madrid, reform/decor blogs (decoesfera-style), administradores-de-fincas publications. Journalists need current local price data every time they write "cuánto cuesta reformar" — be the source.

**Recurring link tracks (2 outreach emails/week):**
- Roundup inclusion: query `intitle:"mejores pintores" madrid` + variants; contact every ranking listicle with proof (review count, insurance, photos). Accept a few paid placements only on sites that actually rank and send traffic.
- Supplier/partner pages: paint-brand registered-applicator directories (Titanlux, Isaval, Bruguer, Jotun), tool/scaffold rental partners, reform companies you subcontract for.
- Founder story: pitch local press + immigrant-entrepreneur angles; podcasts about trades/autónomos in Spain.
- Neighborhood sponsorships: club deportivo, fiestas del barrio, school events → link from their sites + real-world photos.
- HARO-equivalents: respond to journalist requests via Connectively-style services and Spanish PR groups; #JournoRequest on X.

**Refuse:** PBNs, link farms, Fiverr packages, mass guest posts, irrelevant foreign links. Monitor new links monthly (GSC + Ahrefs Starter); disavow only if a spam attack is manifestly hurting.

## 10. Performance & technical hygiene

- Budget: LCP < 2.0s (4G), CLS < 0.05, INP < 200ms. Astro static + Cloudflare makes this trivial — keep it that way (no tag-manager bloat, no chat widgets that load 2MB; use a plain WhatsApp link button).
- Images: AVIF/WebP, `srcset`, lazy-load below the fold, **descriptive Spanish filenames + alt** (`quitar-gotele-salon-chamberi-antes.avif`) — image SEO is real lead flow in this niche ("gotelé antes y después").
- One `<h1>` per page; canonical tags; XML sitemap auto-generated; 404s monitored in GSC.
- `hreflang` pairs only between `/` (es-ES) and `/en/` equivalents that truly exist.
- HTTPS everywhere, HSTS. No interstitials/popups (mobile penalty + they poison AI extraction).
- Quarterly: Screaming Frog crawl (broken links, orphan pages, duplicate titles) + Lighthouse pass + Rich Results re-validation.

## 11. Measurement stack & KPI definitions

| KPI | Tool | Target trajectory |
|---|---|---|
| GBP: calls, direction requests, website clicks | GBP Performance | +20% MoM first year |
| Map-pack presence (home + 5 target zones) | Local rank grid (Local Falcon / SE Ranking maps) | Top-3 home zone by month 6 |
| Organic clicks & queries | GSC | Long-tail page 1 by month 4–6 |
| Reviews: count, velocity, rating | Sheet + GBP | 15–25/month, ≥4.8★ |
| AI mention rate (10 prompts × 4 models) | Monthly manual matrix → later Peec/Otterly | First mentions month 6–9 |
| Leads by source (form, WhatsApp, call, marketplace) | CRM/sheet — ask every lead "¿cómo nos encontraste?" incl. "me lo recomendó ChatGPT" | Organic+GBP = #1 source by month 12 |
| Links/citations earned | Ahrefs Starter + sheet | 3–5 quality links/month after month 4 |

Wire PostHog events: form submit, WhatsApp click, phone click, calculator completion. UTM-tag GBP website link (`?utm_source=gbp`) to separate GBP traffic from pure organic (PostHog reads UTMs natively).

PostHog extras worth wiring once traffic exists: **Surveys** to automate the on-site "¿cómo nos encontraste?" question (answer options incl. "me lo recomendó ChatGPT" — feeds the AI-mention KPI above), and **session replay** (5K free recordings/mo) to watch calculator/quote-form drop-off.

## 12. Build order (engineering checklist)

1. Domains + DNS + email + handle reservations; write `NAP.md`
2. Astro scaffold: layouts, `LocalBusiness` schema component, breadcrumbs, sitemap, robots.txt, llms.txt, IndexNow hook
3. Core pages: home, 7 service pages, /sobre-nosotros, /contacto (with direct-answer blocks + FAQ schema from day one)
4. GBP verification in parallel (can take weeks — start immediately)
5. Price hub + first price guide + calculator
6. Zone data model + template + quality gate + first 8–10 zone pages
7. Projects collection + gallery (feed it after every job)
8. Tier-1 citations sweep (§8)
9. PostHog/GSC/Bing/rank-tracker wiring (§11)
10. English cluster
11. Month 6: price study + PR push; AI-visibility tracking formalized

Everything above is buildable incrementally with Claude Code — the data-file-driven design (§5) is deliberately chosen so adding a zone, project, or price update is a YAML edit + deploy.
