# 05 — CRO Playbook

**The weekly loop for finding and fixing conversion bottlenecks.** Companion to `04-analytics-tracking.md` (event schema, stack). Created 2026-07-14, when ads went live and the CRO instrumentation shipped.

## The stack (what answers which question)

| Question | Tool |
|---|---|
| WHERE do visitors drop? | PostHog funnels (events per `04` §1) |
| WHY do they drop there? | Session replays (masked, sampled) + autocapture heatmaps/dead clicks |
| Which form field blocks people? | `form_abandon.last_field` ranking + `form_error.fields` |
| Did they even see the form/CTA? | `scroll_depth` per template |
| What does paid traffic do differently? | Same funnels filtered `utm_medium = cpc` (ads URL suffix feeds this) |
| Is the page itself slow/broken? | Web vitals (auto-captured) + Cloudflare Worker logs |

Access: PostHog EU project 220433 — UI at eu.posthog.com, or through the PostHog MCP in Claude Code (`claude mcp add --transport http posthog https://mcp.posthog.com/mcp -s user`, OAuth login).

## Funnel definitions (build once, keep stable so weeks compare)

1. **Form funnel (primary)**: `$pageview` → pageview of quote/contact page (`/presupuesto-gratis/`, `/en/free-estimate/`, `/contacto/`, `/en/contact/`) → `form_start` → `form_submit`. Breakdowns: device, locale, `utm_campaign`, landing page.
2. **Service-page conversion**: pageview of `/servicios/*` or `/en/services/*` → any of `whatsapp_click` ∪ `phone_click` ∪ `cta_click` ∪ `form_submit`. Breakdown: service slug, `position`.
3. **Calculator path**: pageview `/precios/` → `calculator_complete` → `whatsapp_click`.

Dashboard **"CRO Semanal"**: the 3 funnels + conversion rate by `utm_campaign` / device / landing page + `form_error` breakdown by `kind`+`fields` + `form_abandon` by `last_field` + web vitals by template.

✅ BUILT 2026-07-14 via the PostHog MCP: dashboard 819228 (pinned) — <https://eu.posthog.com/project/220433/dashboard/819228>. 9 insights tagged `cro` (funnels at last-7-days, friction/web-vitals trends at 30 days; the conversion-rate views are funnels with a single breakdown each). Replay project settings applied the same day: 20% sampling + URL trigger 100% on the four quote/contact paths, match type "any".

## The weekly loop (~30 min, run it with Claude + the PostHog MCP)

1. **Quant — find the drop.** Open the form funnel, last 7 days vs previous 7. Identify the step with the biggest absolute loss, then segment it by device / source / page until a cohort stands out ("mobile paid visitors on /contacto/ drop 80% between form_start and submit").
2. **Qual — watch the drop.** Filter session replays to that exact cohort+step (e.g. sessions with `form_start` but no `form_submit` on mobile). Watch 5–10. Check dead clicks and rage clicks on that template. Read `form_error`/`form_abandon` properties for the same cohort.
3. **Hypothesize.** One sentence: "People abandon at the phone field because the +34 prefix confuses non-Spanish numbers." Score ICE (Impact × Confidence × Ease, 1-5 each). Log it in the table below.
4. **Ship & measure.** At current traffic (~10 paid clicks/day) A/B tests are underpowered — ship the top-ICE fix and compare the funnel step 2 weeks before/after. Reserve PostHog Experiments for ≥100 conversions/variant/month.
5. **Verify & revert.** Next week's loop starts by checking last week's change. No movement → revert or iterate; movement → lock it in and attack the next-biggest drop.

**Discipline rules:** one change per surface per cycle (else you can't attribute the movement); never redefine funnel steps mid-comparison; seasonal weeks (August, Christmas) compare year-not-week.

## Benchmarks (sanity anchors, not goals)

- Quote-page form conversion (form_start → submit): 40-60% is healthy; <25% means a field is hurting.
- Visitor → any conversion on service pages: 3-8% for local services.
- Paid landing conversion (click → lead, all channels incl. WhatsApp/call): 5-10%.

## Change log

| Date | Change | Hypothesis | Result (2w after) |
|---|---|---|---|
| 2026-07-14 | CRO instrumentation shipped (form_start/error/abandon, cta_click, scroll_depth, autocapture, replays) | — baseline — | — |

## Deferred / later

- **Exit-intent survey** on quote pages ("¿Qué te ha impedido pedir presupuesto hoy?") — policy-safe as a dismissible corner widget (Google penalizes blocking interstitials, not corner toasts); enable in PostHog Surveys + flip `disable_surveys` in the Zaraz snippet when wanted.
- **PostHog Experiments** — once traffic supports ~100 conversions/variant/month.
- **Marketing Analytics beta** (blended CPL) — per `04` Phase B+.
