# Aleto Pintores — Analytics & Tracking Doc

**The decided measurement stack and the playbook for activating it.** Companion to `03-seo-guidelines.md` (content rules) and `02-seo-technical-execution.md` (§11 measurement KPIs). Decisions made 2026-07-10.

Guiding constraints, in order: **(1) never compromise site performance** (static, near-zero JS is the product), **(2) GDPR-correct in Spain/EEA**, **(3) no new subscriptions** — everything below is €0 on current volumes.

---

## 1. The decided architecture

| Layer | Tool | Status | Consent needed |
|---|---|---|---|
| Edge/infrastructure metrics | Cloudflare Zone Analytics + Workers observability + AI Crawl Control | ✅ running (automatic) | No |
| Page analytics + real-user Core Web Vitals | **Cloudflare Web Analytics (RUM beacon)** | ⬜ enable in dashboard (one click) | No — cookieless, no personal data |
| SEO / search queries | **Google Search Console** (+ Bing Webmaster) | ⬜ set up ASAP — the SEO source of truth | No |
| Tag manager + CMP + ad/marketing tools | **Cloudflare Zaraz + Zaraz Consent Management** | ⬜ activate at first campaign launch, not before | Yes — Zaraz gates it |
| Ad-platform conversion signals (bidding) | **Google Ads tag + Meta Pixel/CAPI server-side**, via Zaraz tools | ⬜ with Zaraz activation | Yes |
| Attribution & behavioral analytics (the "GA4 role") | **PostHog** (free tier, 1M events/mo) — via Zaraz Custom HTML, consent-gated | ⬜ with Zaraz activation | Yes ("Analítica" purpose) |

**The offline-conversion loop (the highest-leverage ad optimization, decided 2026-07-12):**
1. **Click IDs captured** (live): `gclid`/`wbraid`/`fbclid` are session-persisted by `Attribution.astro` (newest click wins) and attached to every form lead → Sheet columns.
2. **Lead ledger**: the leads Sheet gains stage columns (`quoted` / `won-lost` / `job_value_eur`) filled manually after each conversation (~30 s/lead).
3. **Weekly offline uploads** (at campaign time): won leads (hashed phone + click ID + value) → Google Ads via Aleto Ads Manager (Enhanced Conversions for Leads — the API method already selected in the dashboard) and → Meta CAPI offline events. This makes bidding optimize toward people who HIRE, not people who click.
4. **Call tracking**: use Google Ads' free forwarding numbers on call assets; no CallRail-type subscription.

**Explicitly rejected** (and why, so nobody re-litigates):
- **RudderStack** (evaluated 2026-07-12) — a fine warehouse-first CDP, but Zaraz already plays the capture-once/route-to-many role at the edge for our 3 destinations, free. Revisit only if we need destinations Zaraz can't reach (email tools, warehouse) at real scale.
- **GA4** — user preference; PostHog takes its role (attribution, funnels, events). NOTE: PostHog does NOT feed Google Ads/Meta bidding — that job stays with the platform tags (Google Ads tag, Meta Pixel/CAPI) via Zaraz. Never remove those thinking PostHog covers them.
- **Plausible/Fathom etc.** — good tools, but redundant: RUM covers traffic/CWV now; PostHog covers events/attribution later. No subscription needed.
- **GTM (browser) + standalone certified CMP (CookieYes/Cookiebot/Axeptio)** — the fallback stack, only if Zaraz ever can't run a needed tag or a designer consent UX is wanted. Costs more JS + a vendor.
- **GTM Server-Side for Meta CAPI** — requires a hosted container (~$20–120/mo). Zaraz does CAPI natively at the edge for free.

**PostHog implementation rules (SEO/perf-safe):**
- Loaded as a **Zaraz Custom HTML component**, assigned to the "Analítica" consent purpose → loads ONLY after consent, async/deferred. Crawlers never consent → never see it; the indexed page stays near-zero-JS. LCP/CLS untouched by design.
- **Session recordings OFF or sampled ≤10%** at launch (the rrweb replay module is the heavy part; events-only is light). Disable autocapture extras we don't use (surveys, feature-flag polling).
- **Proxy ingestion through our domain** via a small Worker route (e.g. `aletopintores.com/ph/*` → PostHog cloud) so ad blockers don't eat events (~99% vs ~70% completeness).
- UTMs/referrers auto-captured as first/last-touch person properties → attribution breakdowns on `whatsapp_click`/`form_submit`/`calculator_complete`.
- This is the documented exception to the >15 KB JS guardrail (~50-60 KB, post-consent only). Cloudflare RUM is the independent CWV watchdog — if field INP/LCP degrade after activation, revisit sampling/config.
- OPTIONAL (recommended, can ship pre-campaigns, ~1 KB, first-party): source-stamp leads — capture UTM/referrer in sessionStorage on landing, append a discreet `Ref: <source>` line to WhatsApp prefills and form messages, so each lead arrives already labeled with its true origin. Complements PostHog (attributes the conversation, not just the click).
- DECISION 2026-07-10: PostHog is NOT installed before Zaraz (wizard/npm install rejected — it would ship unconditioned cookies without a CMP). It arrives WITH Zaraz, gated by consent, configured per below.

**PostHog scope — ONLY these (it's a SaaS-analytics suite; we use the lead-gen slice):**

Event schema (fired via `zaraz.track()` → forwarded to PostHog):
| Event | From | Properties |
|---|---|---|
| `whatsapp_click` | WhatsAppButton, CtaBlock, header/footer links | `service`, `page`, `position` (hero/cta/footer), `locale` |
| `phone_click` | `tel:` links | same |
| `form_submit` | ContactForm | `service`, `locale` |
| `calculator_complete` | PriceCalculator | `service`, `m2`, `estimate_range` |

Snippet config:
```js
{
  capture_pageview: true,
  autocapture: false,                  // no click noise; our 4 events are intentional
  person_profiles: 'identified_only',  // visitors stay anonymous — cheaper, less PII
  disable_session_recording: true,     // enable later at ≤10% sampling only to debug funnels
  disable_surveys: true
}
```

Use in the UI: 2 funnels (`pageview → service page → whatsapp_click`; `calculator → whatsapp_click`), 1 leads dashboard (by source / service / page, weekly), the built-in Web Analytics tab. NOT used: feature flags, experiments, surveys, group analytics, data pipelines/CDP, error tracking, heatmaps. Never `identify()` leads with names/phones — client PII stays in WhatsApp, not analytics.

**Phase B+ — PostHog Marketing Analytics (beta) for blended cost-per-lead:**
- Activate only once spend exists on ≥2 channels. Feature is BETA — re-check its pricing/terms at activation.
- **Google Ads + Meta spend**: use PostHog's native connectors (OAuth) — no bucket needed.
- **Marketplace/offline spend** (Habitissimo, Cronoshare — the €100-300/mo playbook line no ad platform sees): drop monthly CSVs (`date, source, cost`) into a **Cloudflare R2 bucket** connected as a self-managed source → true blended CPL across ads + marketplaces in one view.
- R2 cost at our volume: **€0** (10 GB storage + 1M writes/10M reads monthly free tier, zero egress; cost CSVs are KBs). One-time step: R2 activation requires a card on file (no charge within free tier). Later option: automate marketplace-cost uploads with a small Worker.

## 2. Why Zaraz (recorded rationale)

1. **Server-side by design**: tools run in a Worker at Cloudflare's edge → minimal client JS (the whole site currently ships ~0 KB of third-party JS; Zaraz keeps the added weight far below a GTM+CMP+pixels stack).
2. **Real CMP built in**: consent modal, purposes, per-tool gating, consent storage — and it gates **server-side events too** (GDPR applies regardless of where the event fires).
3. **Google Consent Mode v2 automatic** — the EEA requirement for Google Ads conversion/remarketing since March 2024. Cloudflare states Zaraz consent has met Google's EEA ads requirements since March 2024.
4. **Meta Conversions API native**: Pixel ID + CAPI access token in the Zaraz Facebook tool → server-side events with browser/server deduplication. Survives ad blockers/Safari ITP → better EMQ → cheaper leads.
5. Zero additional vendors; same dashboard as hosting; free tier ample at our volume.

**Certification nuance (don't get confused later):** Google's *certified-CMP list* requirement applies to **publishers** (showing AdSense/Ad Manager ads). Aleto is an **advertiser** — the requirement is correct Consent Mode v2 signals, which Zaraz sends. Re-evaluate only if the site ever shows Google ads.

## 3. Activation playbook

### Phase A — now (no consent banner, no JS budget impact worth noting)
1. **Web Analytics**: dashboard → Web Analytics → Add site → `aletopintores.com` → **automatic injection** ON. ⚠️ Do NOT enable "exclude EU visitors from RUM" — our visitors are EU; it would empty the data. (Beacon ≈5 KB, cookieless.)
2. **Google Search Console**: add property, verify via DNS TXT, set geotargeting Spain, submit `https://aletopintores.com/sitemap.xml`. Import into Bing Webmaster Tools (feeds ChatGPT search).
3. Monthly: check AI Crawl Control graphs for GPTBot/ClaudeBot/PerplexityBot activity (free GEO monitoring).

### Phase B — at first campaign launch (Google Ads and/or Meta)

**Status 2026-07-10 — done in advance:**
- ✅ **Site-side event layer live** (`src/components/islands/Attribution.astro` + PriceCalculator/ContactForm): the 4 events fire via `zaraz.track()` (no-op until tools exist) with the §1 property schema; every wa.me prefill is source-stamped (`Ref: <utm or referrer or directo>`, sessionStorage, first-party).
- ✅ **Zaraz consent configured via API**: enabled, purposes `analitica` + `marketing` with ES/EN names/descriptions, branded modal intro + button texts, default language ES, cookie `zaraz-consent`. NOTE: Zaraz does not inject (and the banner does not render) until the FIRST TOOL is added — dormant by design, zero JS on the site today.

**Remaining, blocked on account creation:**
1. Configure tools in Zaraz: Google Ads tag (needs conversion ID/label from a Google Ads account), Facebook Pixel + CAPI access token (needs Meta Business), PostHog as Custom HTML per §1 rules (needs eu.posthog.com project `phc_` key) + the ingestion proxy Worker route. Assign every tool to its purpose (`analitica` → PostHog; `marketing` → Google/Meta).
2. Style the consent modal via `consent.customCSS` to brand tokens (do it when the banner actually renders — needs a tool present).
3. Confirm **Consent Mode v2** signals fire (Zaraz automatic — verify with Tag Assistant).
4. In Google Ads: import `whatsapp_click`/`form_submit`/`phone_click` as conversions; in Meta: map to standard events (Lead, Contact).
5. UTM-tag all paid URLs (`?utm_source=google&utm_medium=cpc&utm_campaign=<c>`); canonical already strips them from indexing. Tag the GBP website link `?utm_source=gbp`.
6. ✅ **Legal (done 2026-07-10)**: `politica-privacidad` rebuilt consent-ready (cookies table: zaraz-consent / Analítica→PostHog EU / Marketing→Google+Meta CAPI; sessionStorage attribution disclosed; DPF transfer note) + EN twin at `/en/privacy-policy/` (hreflang-paired; Zaraz EN modal links to it).
7. **Verify** (all live):
   - No marketing tags fire before consent (Network tab, fresh incognito, deny → zero pixel/collect calls)
   - Consent Mode v2 states update on accept (Tag Assistant)
   - Meta Events Manager shows CAPI events with dedup (same `event_id` browser+server)
   - Lighthouse mobile on `/` stays ≥90 performance with the stack live
   - The consent modal renders correctly in ES and EN

### Guardrails (apply to any future tracking change)
- Nothing loads client-side that can run through Zaraz server-side.
- No tool ships without a consent purpose assigned.
- Any addition that costs >15 KB client JS needs a written justification in this doc.
- RUM/GSC stay outside the consent stack (they need none); do not route them through Zaraz.

## 4. Current Cloudflare zone posture (audited 2026-07-10)

`min_tls_version 1.2` · `always_use_https on` · `early_hints on` · TLS 1.3/HTTP2/HTTP3/Brotli on · 0-RTT off (deliberate) · Rocket Loader/Mirage/Polish off (deliberate — would add risk/JS for nothing) · Managed robots.txt **OFF** (⚠️ was silently injecting `Disallow:` for AI crawlers + `ai-train=no`, killing the GEO strategy — never re-enable; docs/02 §6 governs robots.txt) · AI Crawl Control security: all AI crawlers allowed.

## 5. KPI wiring reference (docs/02 §11)

| KPI | Where it lives |
|---|---|
| GBP calls/clicks | GBP Performance (UTM-tagged link separates GBP traffic in PostHog later) |
| Organic queries/clicks | GSC |
| Page traffic + CWV | Cloudflare Web Analytics |
| Leads by source | Zaraz events → PostHog (UTM person properties) + WhatsApp source-stamping (live) + **lead form → Worker `/api/submit-lead` → Google Sheet** with source/utm/page columns (secret `SHEETS_WEBHOOK_URL` on the worker; graceful 503 fallback until set) + ask every lead "¿cómo nos encontraste?" |
| AI crawler activity | AI Crawl Control |
| AI mention rate | Monthly manual matrix (10 prompts × 4 models) |
