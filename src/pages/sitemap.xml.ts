import type { APIRoute } from 'astro';
import { absolute, getAllIndexablePages } from '@/lib/seo';

/**
 * Custom sitemap with per-URL hreflang alternates. Built from the SAME
 * getAllIndexablePages()/getAlternates() data that renders <head> tags,
 * so sitemap and hreflang can never drift. noindex/gated pages excluded.
 */
export const GET: APIRoute = async () => {
  const pages = await getAllIndexablePages();

  const urls = pages
    .map((p) => {
      const alts =
        p.alternates.length > 1
          ? p.alternates
              .map((a) => `    <xhtml:link rel="alternate" hreflang="${a.hreflang}" href="${a.href}"/>`)
              .join('\n')
          : '';
      const lastmod = p.lastmod ? `    <lastmod>${p.lastmod.toISOString().slice(0, 10)}</lastmod>` : '';
      return [`  <url>`, `    <loc>${absolute(p.path)}</loc>`, lastmod, alts, `  </url>`]
        .filter(Boolean)
        .join('\n');
    })
    .join('\n');

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${urls}
</urlset>
`;

  return new Response(xml, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8' },
  });
};
