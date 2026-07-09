# Aleto Pintores — SEO Content Guidelines (Operating Manual)

**Every future page, edit and translation follows this document.** It encodes how this site keeps its SEO quality as it grows. Companion docs: `01-seo-strategy-playbook.md` (strategy), `02-seo-technical-execution.md` (technical spec). The site implements both; this doc is the day-to-day manual.

---

## 1. The golden rule: content and meta live in ONE place

Meta tags are **never** written in templates. Every `<title>`, meta description, date, FAQ, hreflang pair and price on the site derives from:

| What | Single source of truth | Consumed by |
|---|---|---|
| Title, description, H1, direct answer, FAQ, dates | Frontmatter of the page's content file (`src/content/…`) | `<head>` meta, OG/Twitter tags, FAQPage schema, sitemap `lastmod` |
| Prices | `src/data/precios.yaml` | Price tables, calculator, Service schema `offers`, llms.txt, hub summary table |
| NAP (name, address, phone) | `NAP.md` → mirrored in `src/data/business.ts` | Footer, contact page, LocalBusiness schema, llms.txt |
| Zone data | `src/data/zonas/*.yaml` | Zone pages, their FAQ + schema |

**Consequence: to change what a page says AND how it appears in Google, you edit exactly one file.** If you ever find yourself editing a meta tag inside a `.astro` template, stop — you're breaking the system.

### The build enforces meta quality (zod = meta linter)

`src/content.config.ts` fails the build when:
- `title` is under 15 or over 60 chars (SERP truncation limit)
- `metaDescription` is under 70 or over 160 chars (Google's display window)
- `directAnswer` is under 80 or over 500 chars
- required fields are missing

A failed build with `InvalidContentEntryDataError` means a frontmatter field violates these rules. Fix the content, not the schema.

## 2. Editing an existing page — checklist

1. Edit the markdown body and/or frontmatter in `src/content/<collection>/<locale>/<slug>.md`.
2. If the meaning of the page changed, update `title`, `metaDescription` and `directAnswer` to match — they must always describe the current content.
3. **Always bump `dateModified`** to today. This updates the visible "Actualizado:" line, `article:modified_time`, WebPage schema `dateModified` and the sitemap `lastmod`. Freshness is a ranking and AI-citation factor.
4. `npm run build` — zod validates your meta.
5. If prices changed, that edit belongs in `src/data/precios.yaml`, not in prose. Body text may cite numbers, but keep them consistent with the YAML (grep for the old number to catch stale mentions).

## 3. Writing a NEW page — the recipe (docs/02 §3)

Structure, in this exact order (the layouts enforce most of it):

1. **H1 = the search query**, natural-language ("Quitar gotelé y alisar paredes en Madrid"). One H1 per page, always.
2. **`directAnswer` frontmatter**: 2–3 sentences with **concrete numbers** answering the query directly. This is what featured snippets and AI assistants quote verbatim. Formula: *[thing] cuesta entre X € y Y € en [año], [what's included]. [One qualifier sentence].*
3. **Price table** — automatic from `priceKey`.
4. **Body: question-phrased `<h2>`s** ("¿Cuánto cuesta…?", "¿Se puede…?"), each section **self-contained, 100–170 words**, answering its own H2 completely. This is the format generative engines lift most reliably.
5. **FAQ frontmatter: 5–8 real questions** clients actually ask. These render visibly AND become FAQPage schema — never add schema-only FAQs.
6. CTA comes from the layout.

Style rules:
- Numbers over adjectives. "9–15 €/m²" beats "precios competitivos". Evidence-dense content is cited 30–40% more by AI models.
- Every stat gets a source or methodology note ("según nuestros presupuestos de 2026").
- Internal links inside body text: service ↔ its price guide (both directions), related services, zone pages when they exist. 2–4 contextual links per page.
- No filler posts. A blog entry must name its `targetQuery` in frontmatter — if you can't, don't write it.

## 3b. Copy angles & the 15% price rule

**Prose sells certainty; the meta layer sells price.** On service pages, home and about, price is ≈15% of the visible prose: max ONE price-context section per page (framed as certainty — "precio cerrado que no crece" — and linking to the `/precios/` guide for the numbers) and ≤2 price FAQs. The `/precios/` cluster is exempt — price is its search job.

The meta layer keeps its price hooks regardless: `title`, `metaDescription` and `directAnswer` retain concrete numbers, because they feed SERP snippets, featured snippets and AI answers. The `PriceTable` component stays on service pages (it's data, not prose).

**The angle library** — the real reasons demanding clients choose a painter. Every body section should serve one:
1. **Who's in my home** — same named crew start to finish, insured, direct contact
2. **The protection protocol** — sealed rooms, dust extraction, wrapped furniture, daily cleanup, odourless paints
3. **Prep is the finish** — 70% happens before paint; raking-light (luz rasante) as the verifiable standard
4. **Dates that hold** — start/delivery dates in writing; the fixed quote lives here as ONE certainty signal
5. **Materials & building fluency** — right system per substrate; classic-Madrid expertise (old plaster, mouldings, 3 m ceilings)
6. **Never in the dark** — one contact, photo updates, no decisions without the client
7. **Color confidence** — real samples on the client's walls, advice per room's light
8. **Aftercare** — written warranty honored, labeled leftover paint, revisions/checkups

For architects/interior designers (see `/para-arquitectos-e-interioristas/`): spec fidelity (color/sheen/flatness), in-situ samples before execution, trade coordination and signed deadlines, complete documentation, "we make the studio look good with its client".

## 4. Adding pages, step by step

### New service
1. Add the price entry in `src/data/precios.yaml` (label_es/label_en, unidad, min/max, ejemplos).
2. Create `src/content/servicios/es/<keyword-slug>.md` with full frontmatter (`translationKey: service-<name>`, `priceKey`, `proceso`, `relatedServices`, FAQ).
3. Optionally its price guide in `src/content/precios/es/precio-<slug>.md`.
4. Build. The service auto-appears in hubs, home grid, calculator, llms.txt and sitemap.

### English version of any page
Create the same file under `en/` with an **English-keyword slug** and the **same `translationKey`**. That's all: hreflang pairs (both directions + x-default), sitemap alternates and the header language switcher all light up automatically. Never translate slugs literally — use the slug English searchers would type.

### New zone page (programmatic SEO — docs/02 §5)
1. Create `src/data/zonas/<slug>.yaml` with ALL fields: `vivienda` (≥80 chars of real housing-stock knowledge), `notas_precio`, `precio_pintar_piso_80m2` from real quotes, `barrios`.
2. **The quality gate requires ≥1 real project or ≥2 zone reviews.** Without local proof the page will not build — this is deliberate (doorway-page penalty protection). Never fake proof to pass the gate; do a job in the zone first.
3. Reference the project/review ids in the yaml. Build → page + sitemap entry appear.
4. Rollout discipline: launch zones only as jobs create proof; cap ~21 distritos + 15–20 municipios.

### New project (gallery)
1. Photos → `public/img/proyectos/`, named descriptively in Spanish: `quitar-gotele-salon-chamberi-antes.avif` (this naming IS image SEO — "gotelé antes y después" searches convert).
2. Every image needs a descriptive Spanish `alt`.
3. Create `src/content/proyectos/<slug>.md`: zone, services, m², real price, days, ≥2 images (schema-enforced).
4. First real project: set `noindex: false` in `src/content/paginas/es/proyectos-hub.md` so the gallery starts indexing.

### First reviews
Add `src/data/reviews/*.yaml`; at ≥3 reviews set `noindex: false` in `paginas/es/opiniones.md`.

## 5. Quarterly price update (freshness ritual)

1. Recompute ranges from real quotes → edit `src/data/precios.yaml`, bump its `dateModified`.
2. Bump `dateModified` in each `precios/` guide (and adjust any prose citing old numbers — grep the old figures).
3. Update the year in titles/H1s each January ("precios 2027").
4. Build + deploy. Tables, calculator, schema offers and llms.txt update from the YAML automatically.

## 6. NAP changes (rare, critical)

`NAP.md` first → then `src/data/business.ts` → then every external citation (GBP, directories — checklist docs/02 §8). The footer, schema and llms.txt update from `business.ts` automatically. Never write address/phone inline anywhere else.

When social/directory profiles are created, add their URLs to `sameAs` in `business.ts` — it's the entity-resolution glue for Google and AI models. Only ever list profiles that actually exist.

## 7. Google Ads landing-page quality (why this system scores well)

Quality Score = expected CTR + ad relevance + **landing page experience**. Every page here is built for it:
- **Message match**: H1 = the query = the ad group keyword. Point ads at the specific service/price page, never the home page.
- **Speed**: static HTML, ~0 JS on content pages. Keep it that way — no tag managers, no chat widgets, no popups (they also poison AI extraction).
- **Prices visible** above the fold (directAnswer + table) — strongest relevance signal for "precio" queries and best pre-qualifier for leads.
- UTM discipline: tag ad URLs (`?utm_source=google&utm_medium=cpc&utm_campaign=<c>`); canonical strips them from indexing.
- New campaign landing pages: create them as `precios/` or `servicios/` entries with `noindex: true` if they shouldn't rank organically — they still get full meta/speed treatment.

## 8. Indexing gates — current state at launch

| Page | State | Opens when |
|---|---|---|
| `/pintores/{zona}/` | not built | zone yaml passes quality gate (§4) |
| `/proyectos/` | noindex | first project published + flip `noindex` in `paginas/es/proyectos-hub.md` |
| `/opiniones/` | noindex | ≥3 reviews + flip `noindex` in `paginas/es/opiniones.md` |
| `/blog/` | noindex | first post + flip `noindex` in `paginas/es/blog-hub.md` |
| Legal pages | noindex | stays noindex forever |

The sitemap excludes all noindex pages automatically.

## 9. Verification before every deploy

```bash
npm run build          # zod meta-lints every page; fails on violations
npx astro check        # TypeScript
```
Spot-check `dist/`: one `<title>`/canonical/H1 per page; hreflang only on true pairs; JSON-LD parses (Rich Results Test on one page per template quarterly).

**Cache gotcha:** if you *delete* a content/data file and its page keeps building, clear the content-layer cache: `rm -rf node_modules/.astro .astro dist && npm run build`.

### Preview environments (duplicate-content protection)

The only indexable host is `aletopintores.com`. Three layers keep preview/dev URLs out of Google:
1. `public/_headers` sends `X-Robots-Tag: noindex` on every `*.pages.dev` host (production alias and branch previews). Verify after deploy: `curl -sI https://<project>.pages.dev/ | grep -i x-robots-tag` → `noindex`; the same curl on `aletopintores.com` must show **no** such header.
2. Every page's canonical is an absolute `https://aletopintores.com/...` URL, so even a crawled preview points Google at production.
3. After the custom domain goes live, uncomment the 301 rule in `public/_redirects` so `pages.dev` URLs redirect to the real domain outright.

Never share or link `pages.dev` URLs publicly (social bios, directories, GBP) — always the real domain.

## 10. What we never do

- Meta tags or NAP hand-written in templates
- FAQ schema for questions not visible on the page
- `aggregateRating` markup (until genuine first-party reviews render on-page — and even then, never from Google reviews)
- Zone pages without local proof, or launched in bulk
- Auto-redirect by browser language (banner suggestion only — redirects poison indexing)
- Interstitials, popups, heavy third-party scripts
- Buying reviews or links (docs/01 §6, §8)
