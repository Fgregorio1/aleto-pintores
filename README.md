# Aleto Pintores

A high-performance, SEO-optimized static web application for **Aleto Pintores** built with Astro and styled with TailwindCSS, utilizing a Cloudflare Worker for first-party analytics (PostHog proxy) and lead ingestion.

---

## 🚀 Local Development

To run the Astro dev server locally:

```bash
npm run dev
```

---

## 📊 Google Sheets Webhook Test

To verify that the Google Sheets Apps Script webhook is online and accepting lead data, you can run the test script:

```bash
python3 scripts/test_connection.py
```
*(Note: To run a custom local mock lead submission, use the scratch script `/Users/felipegregorio/.gemini/antigravity-cli/brain/3ab32a32-b790-43e3-9b1d-f9d5a10fa75c/scratch/test_sheet.py`)*

---

## 📈 Offline Conversion Uploads

When you close a sale, record the customer's Google Click ID (`gclid` / `wbraid`), the job value in EUR, and the closing date and time. Save these in a CSV file (e.g., `won_leads.csv`) structured like this:

```csv
gclid,value,time
gclid_value_1,1500,2026-07-13 14:30:00+02:00
gclid_value_2,2200,2026-07-13 18:00:00+02:00
```

Then, run the built-in script using your specific conversion action ID (`7683879771`):

```bash
python3 scripts/upload_conversions.py path/to/won_leads.csv 7683879771
```

This tells Google Ads which clicks generated actual business, optimizing your smart bidding strategy.
