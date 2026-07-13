# Google Ads Assistant Operating Prompt — Aleto Pintores

This prompt guide is configured to direct AI coding assistants in managing and optimizing Google Ads for aletopintores.com.

---

## 0. Connect to Google Ads API
> Read the setup guide and walk me through connecting the Google Ads API client. My Google Ads Customer ID is `183-132-6341` (Google Tag: `AW-18313263418`).

---

## 1. Build the Search Campaigns
> Build two Search campaigns:
> 1. **Aleto Pintores - Madrid (Spanish)**: Targeting painting, gotelé removal, and lacquering in Madrid.
> 2. **Aleto Pintores - Expat Madrid (English)**: Targeting English-speaking expats, landlords, and tenants in Madrid.
> Set both campaigns to PAUSED until I approve.

---

## 2. Build the Responsive Search Ads (RSAs)
> Build high-performing Responsive Search Ads (RSAs) for the following Ad Groups:
> * **Ad Group: Pintar Piso Madrid (Spanish)** (Target: `/servicios/pintura-interior-pisos/`)
> * **Ad Group: Quitar Gotelé Madrid (Spanish)** (Target: `/servicios/quitar-gotele-alisar-paredes/`)
> * **Ad Group: Expat Painters Madrid (English)** (Target: `/en/services/interior-painting-madrid/`)
> Incorporate value propositions like: budget cerrado en 24h, plazos por contrato, seguro Mapfre (300k €), and client support in English. Add the ads as PAUSED.

---

## 3. Negative Keywords Setup
> Create a Shared Negative Keyword List named "Aleto Universal Negatives" and attach it to both campaigns. Populate it with standard junk search terms (DIY, gratis, empleo, leroy merlin, bricomart, foro, etc.) using broad or phrase matches where appropriate.

---

## 4. Landing Page Configuration Audit
> Audit the Astro service layout files. Confirm that the contact form passes `gclid`, `wbraid`, `gbraid`, `fbclid`, and all standard UTMs (`utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`, `utm_id`) in its JSON payload to the worker endpoint `/api/submit-lead`.

---

## 5. Verify Conversion Tracking & Enhanced Conversions
> Verify that the Google Tag (`AW-18313263418`) is loaded in the Astro base layout head. Verify that on form success, the LeadForm triggers the conversion event with `'send_to': 'AW-18313263418/YIMKCLb24s8cELryuJxE'` and supplies client email and phone inside `'enhanced_conversion_data'` for secure hashing, before executing the redirect callback.

---

## 6. Check Tag Assistant Logs
> Can you verify that the conversion event fires successfully based on the payload strings copied from Google Tag Assistant on the success redirect paths `/gracias/` or `/en/thank-you/`?

---

## 7. Build an Ads Analytics Dashboard
> Build a simple analytics dashboard at `/dashboard` in the Astro site. Parse campaign ROAS, leads generated, and match rate recommendations, locking it under custom admin access.

---

## 8. Find Search Terms Bleeding Money
> Pull search term reports for the painting campaigns. Analyze keywords that spend budget but have zero conversions, and suggest them as negatives.

---

## 9. Deploy & Verify
> Push the updated repository to GitHub to trigger the Cloudflare Pages deploy. Once deployed, run a network check on the live site to confirm the Google Tag and conversion event setup execute flawlessly.



