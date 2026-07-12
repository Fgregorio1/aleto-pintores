/**
 * Worker script — handles ONLY /api/* and /ph/* (see wrangler.jsonc
 * run_worker_first). Every other route is served directly from static
 * assets and never invokes this code.
 *
 * POST /api/submit-lead: validates the estimate form and forwards the lead
 * to a Google Sheets Apps Script webhook (SHEETS_WEBHOOK_URL secret).
 * Ported from cm-painting-website/src/pages/api/submit-lead.ts, without
 * Astro/zod dependencies.
 *
 * /ph/*: reverse proxy to PostHog EU ingestion (official Cloudflare recipe,
 * https://posthog.com/docs/advanced/proxy/cloudflare) so analytics events
 * are first-party and survive ad blockers. Configure the PostHog snippet
 * with api_host: 'https://aletopintores.com/ph', ui_host: 'https://eu.posthog.com'.
 */

interface Env {
  ASSETS: Fetcher;
  SHEETS_WEBHOOK_URL?: string;
  SHEETS_SHARED_TOKEN?: string;
}

const json = (status: number, body: Record<string, unknown>) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
  });

/** Phone validation: E.164; for +34 require 9 digits starting 6/7/8/9 */
function validPhone(e164: string): boolean {
  if (!/^\+\d{7,15}$/.test(e164)) return false;
  if (e164.startsWith('+34')) return /^\+34[6789]\d{8}$/.test(e164);
  return true;
}

interface LeadFields {
  full_name: string;
  email: string;
  phone: string;
  phone_country: string;
  zip_code: string;
  service: string;
  form_source: string;
  privacy: string;
  source: string;
  utm_source: string;
  utm_medium: string;
  utm_campaign: string;
  gclid: string;
  wbraid: string;
  fbclid: string;
  page: string;
  locale: string;
  company: string; // honeypot
}

function validate(d: LeadFields): { field: string; error: string } | null {
  if (!d.full_name || d.full_name.trim().length < 2) return { field: 'full_name', error: 'name' };
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(d.email)) return { field: 'email', error: 'email' };
  if (!validPhone(d.phone)) return { field: 'phone', error: 'phone' };
  if (d.zip_code && !/^\d{4,5}$/.test(d.zip_code)) return { field: 'zip_code', error: 'zip' };
  if (!d.service) return { field: 'service', error: 'service' };
  if (d.privacy !== 'true') return { field: 'privacy', error: 'privacy' };
  return null;
}

async function submitLead(request: Request, env: Env): Promise<Response> {
  let d: LeadFields;
  try {
    d = (await request.json()) as LeadFields;
  } catch {
    return json(400, { success: false, error: 'bad_json' });
  }

  // Honeypot: bots fill the hidden "company" field — accept silently, forward nothing
  if (d.company) return json(200, { success: true });

  const invalid = validate(d);
  if (invalid) return json(422, { success: false, ...invalid });

  if (!env.SHEETS_WEBHOOK_URL) {
    // Webhook not configured yet — tell the client to offer the WhatsApp fallback
    return json(503, { success: false, setup: false });
  }

  const record = {
    timestamp: new Date().toISOString(),
    full_name: d.full_name.trim(),
    email: d.email.trim(),
    phone: d.phone,
    phone_country: d.phone_country || 'ES',
    zip_code: d.zip_code || '',
    service: d.service,
    form_source: d.form_source || 'home',
    locale: d.locale || 'es',
    page: d.page || '',
    source: d.source || 'directo',
    utm_source: d.utm_source || '',
    utm_medium: d.utm_medium || '',
    utm_campaign: d.utm_campaign || '',
    gclid: d.gclid || '',
    wbraid: d.wbraid || '',
    fbclid: d.fbclid || '',
    ip_address: request.headers.get('CF-Connecting-IP') || '',
    user_agent: request.headers.get('User-Agent') || '',
    ...(env.SHEETS_SHARED_TOKEN ? { token: env.SHEETS_SHARED_TOKEN } : {}),
  };

  try {
    // Apps Script answers POSTs with a 302 to a googleusercontent echo URL;
    // follow it manually with a GET to read the JSON reply (same as CM's worker).
    let res = await fetch(env.SHEETS_WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(record),
      redirect: 'manual',
    });
    if (res.status >= 300 && res.status < 400) {
      const loc = res.headers.get('Location');
      if (loc) res = await fetch(loc, { method: 'GET' });
    }
    if (!res.ok) return json(502, { success: false, error: 'webhook_failed' });
    return json(200, { success: true });
  } catch {
    return json(502, { success: false, error: 'webhook_unreachable' });
  }
}

// ── PostHog reverse proxy ──────────────────────────────────────────────
const POSTHOG_API_HOST = 'eu.i.posthog.com';
const POSTHOG_ASSET_HOST = 'eu-assets.i.posthog.com';

async function posthogProxy(request: Request, ctx: ExecutionContext): Promise<Response> {
  const url = new URL(request.url);
  // strip the /ph mount prefix, keep the rest of the path + query string
  const pathWithParams = url.pathname.replace(/^\/ph/, '') + url.search;

  if (pathWithParams.startsWith('/static/')) {
    // Static assets: cache at the edge (per PostHog's official worker)
    let response = await caches.default.match(request);
    if (!response) {
      response = await fetch(`https://${POSTHOG_ASSET_HOST}${pathWithParams}`);
      ctx.waitUntil(caches.default.put(request, response.clone()));
    }
    return response;
  }

  // Ingestion/API: forward method/body/headers, but never our zone's cookies
  const originRequest = new Request(request);
  originRequest.headers.delete('cookie');
  return fetch(`https://${POSTHOG_API_HOST}${pathWithParams}`, originRequest);
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === '/api/submit-lead') {
      if (request.method !== 'POST') return json(405, { success: false, error: 'method' });
      return submitLead(request, env);
    }
    // Any other /api path → 404
    if (url.pathname.startsWith('/api/')) return json(404, { success: false, error: 'not_found' });
    // PostHog ingestion proxy (first-party analytics)
    if (url.pathname.startsWith('/ph/')) return posthogProxy(request, ctx);
    // Paths outside run_worker_first never reach this script
    return env.ASSETS.fetch(request);
  },
} satisfies ExportedHandler<Env>;
