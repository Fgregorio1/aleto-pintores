# Cloudflare zone configuration — aletopintores.com

Settings that live in the Cloudflare dashboard/API, NOT in this repo (zone
`22d39316b7ed8f2f7e867c75fb438340`, account `c88951c3fc2ce4a5742039071fd202df`).
Updated 2026-07-12 after a full zone audit.

## Speed / delivery
- HTTP/3, TLS 1.3 (min 1.2), Brotli, Early Hints, IPv6: **on**
- **Speed Brain: on** (2026-07-12) — Speculation Rules prefetch on link hover.
  Safe here: fully static site, the worker only mutates on POST (`/api/*`).
- Rocket Loader, Mirage, Polish: **off** (paid/breaks-things; astro:assets
  handles images at build time)
- Tiered Cache / Argo: **off on purpose** — Workers static assets have no
  origin to shield; enabling buys nothing.
- Browser cache TTL 4 h for HTML; `/_astro/*` immutable 1 y via `public/_headers`.

## Email (added 2026-07-12)
- **Email Routing enabled**: MX route1-3.mx.cloudflare.net + SPF
  `v=spf1 include:_spf.mx.cloudflare.net ~all` (Cloudflare-managed records).
- Forwarding rule `contacto@aletopintores.com` → gregorio.inov@gmail.com is
  configured in the dashboard (destination address requires email verification;
  the API token has no account-level Email Routing scope).
- **DMARC**: TXT `_dmarc` = `v=DMARC1; p=quarantine;
  rua=mailto:gregorio.inov@gmail.com; adkim=r; aspf=r` — quarantines spoofed
  mail. If we later send AS contacto@ via Gmail, add Gmail's SPF include and
  consider moving to `p=reject` once reports are clean.
- Receive-only today. Replies go out from the Gmail address.

## Security
- WAF: Cloudflare Managed Free Ruleset; security level medium; DDoS L7 default.
- Bot Fight Mode / AI bot blocking: **off on purpose** — AI crawlers are
  deliberately allowed for GEO visibility (docs/seo). Don't "fix" this.
- HSTS + security headers come from `public/_headers`, not zone settings.
- No CSP header: would break Zaraz/PostHog inline scripts — its own project.
- No CAA records: Cloudflare rotates CAs for edge certs; a stale CAA list can
  block renewals. Leave unset.

## Crawl / indexing
- AI Crawl Control: all AI crawlers allowed.
- Crawler Hints: not enabled — redundant with our own IndexNow cron
  (worker `scheduled` handler, daily 06:00 UTC, key file in `public/`).
- www → apex 301: zone Redirect Rule ("Redirect from WWW to Root" template).
  Workers `_redirects` cannot do host rules (deploy error 100324).

## DNS records (beyond Cloudflare-managed email set)
- `AAAA aletopintores.com` + `www` → `100::` proxied (Workers custom domains)
- `TXT` google-site-verification (GSC)
- `TXT _dmarc` (see Email above)
