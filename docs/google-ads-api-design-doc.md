# Aleto Ads Manager — Design Documentation

**Google Ads API Developer Token Application — Tool Design Document**

| | |
|---|---|
| **Tool name** | Aleto Ads Manager |
| **Company** | Aleto Pintores — residential & commercial painting services, Madrid, Spain |
| **Website** | https://aletopintores.com |
| **Contact** | contacto@aletopintores.com |
| **Tool category** | **Internal, in-house tool.** Used exclusively to manage the advertising accounts owned by Aleto Pintores. Not offered, sold, licensed or exposed to any third party. |
| **Requested access** | Basic access |
| **Date** | July 2026 |

---

## 1. Purpose

Aleto Ads Manager is an internal tool that helps the owner of Aleto Pintores (a small painting business) create, manage and report on the company's **own Google Ads Search campaigns**. The tool is AI-assisted: a large-language-model agent (Anthropic Claude, operated through the Claude Code environment) drafts campaign structures, ad copy and optimization proposals. **Every change that would modify the account (mutate operation) is reviewed and explicitly approved by the business owner before the tool executes it.** The AI proposes; a human decides.

The tool exists because the business is owner-operated with no marketing staff: AI assistance makes professional campaign management feasible, while API access makes changes auditable, scripted and reversible instead of manual dashboard edits.

## 2. Users and account scope

- **Single user:** the business owner (and only the owner).
- **Single advertiser:** the tool authenticates exclusively against the Google Ads account(s) owned by Aleto Pintores, under the company's own manager (MCC) account.
- The developer token will never be used to access accounts of any other company or client. The tool is not a service offered to others; there is no signup, no multi-tenant capability, and no plan to resell or white-label it.

## 3. Functional description

### 3.1 What the tool does

1. **Campaign creation** — builds Search campaigns for the company's painting services (interior painting, gotelé removal, door lacquering, facade painting) targeting Madrid, Spain: campaigns, ad groups, keywords, negative keywords, responsive search ads, sitelinks and budgets.
2. **Campaign management** — pauses/enables entities, adjusts budgets and bids (Smart Bidding configurations), updates ad copy, adds negative keywords derived from search-term reports.
3. **Reporting** — retrieves performance reports (impressions, clicks, cost, conversions, search terms) for internal analysis and for the owner's weekly review.
4. **Conversion management** — creates and maintains the company's own conversion actions (WhatsApp click, phone click, quote-form submission), which are fired from the company website.

### 3.2 What the tool deliberately does NOT do

- No access to third-party accounts; no cross-account data mixing.
- No automated spend increases: budget changes always require explicit owner approval.
- No scraped or purchased audience data; no upload of third-party user data.
- No fully autonomous mutations: the AI agent cannot execute a mutate call without a human approval step (see §5).

## 4. Architecture

```
+----------------+     conversation      +---------------------+
| Business owner | <------------------>  |  AI agent (Claude)  |
| (approves all  |    proposals /        |  drafts campaigns,  |
|  mutations)    |    approvals          |  analyses reports   |
+----------------+                       +---------------------+
                                                    |
                                                    v
                                         +---------------------+
                                         |  API client layer   |
                                         |  (Python,           |
                                         |  google-ads-python  |
                                         |  official library)  |
                                         +---------------------+
                                                    |
                                     OAuth 2.0 (company credentials)
                                     Developer token (this application)
                                                    |
                                                    v
                                         +---------------------+
                                         |   Google Ads API    |
                                         |   (own MCC account) |
                                         +---------------------+
```

- **Runtime:** local workstation scripts (Python, official `google-ads` client library). No public-facing servers; no hosted SaaS component.
- **Authentication:** standard OAuth 2.0 installed-application flow with credentials from the company's own Google Cloud project; refresh token for the company's own Ads login. The developer token is used only in combination with these company-owned credentials.
- **Reporting path is read-only;** the mutation path is separated and wrapped by the approval step described in §5.

## 5. Human-in-the-loop control for AI-generated changes

All mutate operations follow a fixed workflow:

1. The AI agent prepares a **change proposal** (e.g., "create ad group 'Quitar gotelé — Chamberí' with these 12 keywords, this RSA copy, budget X €/day") rendered as a human-readable diff.
2. The owner reviews and **explicitly approves or rejects** the proposal in the console.
3. Only after approval does the client layer execute the corresponding API calls, using `validateOnly` pre-checks where applicable.
4. Every executed change is **logged locally** (timestamp, entities affected, request summary) so the account history is fully auditable and reversible.

## 6. Google Ads API services used

| Service | Use |
|---|---|
| GoogleAdsService (SearchStream) | Reporting: campaign/ad group/keyword/search-term performance |
| CampaignService, CampaignBudgetService | Create/manage Search campaigns and budgets |
| AdGroupService, AdGroupCriterionService | Ad groups, keywords, negative keywords |
| AdGroupAdService | Responsive search ads |
| AssetService / campaign & ad group asset services | Sitelinks, callouts, structured snippets |
| ConversionActionService | The company's own conversion actions |
| KeywordPlanIdeaService | Keyword research for the company's services |
| RecommendationService | Review (not auto-apply) of Google recommendations |

Expected volume: very low — a single small account; tens of mutate operations per week at most, well within Basic access limits.

## 7. Data handling, privacy and security

- **Data accessed:** only the company's own campaign structures and performance metrics. No end-user personal data is retrieved through the API.
- **Storage:** API credentials (developer token, OAuth client, refresh token) are stored in a local, git-ignored configuration file on the owner's machine. Reports are stored locally for internal analysis only.
- **No sharing or resale** of any API data. No co-mingling with data from other advertisers (there are none).
- Website-side conversion tracking operates under a consent-management platform (Google Consent Mode v2) in compliance with EU/GDPR requirements.

## 8. Compliance statement

- The tool is an **internal-use tool for a single advertiser** (the token holder's own company). It is not a third-party or full-service tool; accordingly, Required Minimum Functionality obligations for third-party tools do not apply. Should the tool's scope ever change, we will re-apply/notify Google as required.
- The tool will comply with the **Google Ads API Terms and Conditions** and Google Ads policies, including the AI-generated content being subject to the same editorial review and policy checks as human-written ads (a human reviews all ad copy before it is submitted).
- Contact for API matters: contacto@aletopintores.com.
