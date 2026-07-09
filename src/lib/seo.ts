import { getCollection, type CollectionEntry } from 'astro:content';
import { SITE_URL } from '@/data/business';
import { staticRoute, type StaticRoute } from '@/i18n/routes';
import type { Locale } from '@/i18n/ui';
import { collectionPath, entryLocale } from './paths';
import { blogIndexable, proyectosIndexable, zonaPassesGate } from './gates';

/**
 * The meta engine. Pages NEVER write <head> tags themselves — they build an
 * SEOData (usually via seoFromEntry / seoFromPagina) and hand it to
 * <BaseLayout seo={...}>. Because SEOData is derived from frontmatter,
 * editing content frontmatter is the one and only way meta changes.
 *
 * getAlternates() is also the ONLY source of hreflang pairs, used both by
 * the <head> and by sitemap.xml — the two can never drift.
 */

export interface Alternate {
  hreflang: string;
  href: string; // absolute
}

export interface SEOData {
  title: string;
  description: string;
  canonicalPath: string;
  locale: Locale;
  alternates: Alternate[];
  noindex?: boolean;
  ogImage?: string;
  ogType?: 'website' | 'article';
  datePublished?: Date;
  dateModified?: Date;
  /** default true → title rendered as "{title} | Aleto Pintores" */
  brandSuffix?: boolean;
}

export const BRAND_SUFFIX = 'Aleto Pintores';
export const DEFAULT_OG_IMAGE = '/img/og-default.jpg';

export function absolute(path: string): string {
  return new URL(path, SITE_URL).href;
}

function hreflangFor(locale: Locale): string {
  return locale === 'es' ? 'es-ES' : 'en';
}

/** Build the alternates list from the ES/EN paths of one logical page. */
function buildAlternates(esPath?: string, enPath?: string): Alternate[] {
  const alts: Alternate[] = [];
  if (esPath) alts.push({ hreflang: 'es-ES', href: absolute(esPath) });
  if (enPath) alts.push({ hreflang: 'en', href: absolute(enPath) });
  // x-default → Spanish (the site's default experience); only meaningful when a real pair exists
  if (esPath && enPath) alts.push({ hreflang: 'x-default', href: absolute(esPath) });
  return alts;
}

type I18nCollection = 'servicios' | 'precios';

/** hreflang pair for a collection entry: exists iff both locales share the translationKey. */
export async function getAlternates(
  collection: I18nCollection,
  translationKey: string,
): Promise<Alternate[]> {
  const entries = await getCollection(
    collection,
    (e: CollectionEntry<I18nCollection>) => e.data.translationKey === translationKey && !e.data.draft,
  );
  const es = entries.find((e) => entryLocale(e.id) === 'es');
  const en = entries.find((e) => entryLocale(e.id) === 'en');
  const pair = buildAlternates(
    es ? collectionPath(collection, es) : undefined,
    en ? collectionPath(collection, en) : undefined,
  );
  return pair;
}

/** hreflang pair for a one-off page registered in src/i18n/routes.ts */
export function getStaticAlternates(routeKey: string): Alternate[] {
  const r: StaticRoute = staticRoute(routeKey);
  return buildAlternates(r.es, r.en);
}

/** SEOData from a servicios/precios collection entry. */
export async function seoFromEntry(
  collection: I18nCollection,
  entry: CollectionEntry<I18nCollection>,
): Promise<SEOData> {
  return {
    title: entry.data.title,
    description: entry.data.metaDescription,
    canonicalPath: collectionPath(collection, entry),
    locale: entryLocale(entry.id),
    alternates: await getAlternates(collection, entry.data.translationKey),
    noindex: entry.data.noindex || entry.data.draft,
    ogImage: entry.data.ogImage ?? DEFAULT_OG_IMAGE,
    ogType: 'website',
    datePublished: entry.data.datePublished,
    dateModified: entry.data.dateModified,
  };
}

/** SEOData from a `paginas` entry (one-off pages — home, about, contact, hubs, legal). */
export function seoFromPagina(entry: CollectionEntry<'paginas'>, opts?: { noindexOverride?: boolean }): SEOData {
  const locale = entryLocale(entry.id);
  const r = staticRoute(entry.data.pageKey);
  return {
    title: entry.data.title,
    description: entry.data.metaDescription,
    canonicalPath: locale === 'en' ? (r.en ?? r.es) : r.es,
    locale,
    alternates: getStaticAlternates(entry.data.pageKey),
    noindex: opts?.noindexOverride ?? (entry.data.noindex || entry.data.draft),
    ogImage: entry.data.ogImage ?? DEFAULT_OG_IMAGE,
    ogType: 'website',
    datePublished: entry.data.datePublished,
    dateModified: entry.data.dateModified,
  };
}

/** SEOData for blog/proyectos/zonas entries (single-locale for now). */
export function seoFromSingleLocale(
  collection: 'blog' | 'proyectos' | 'zonas',
  entry: any,
  extra?: Partial<SEOData>,
): SEOData {
  const path = collectionPath(collection, entry);
  const d = entry.data;
  return {
    title: d.title ?? d.nombre,
    description: d.metaDescription ?? '',
    canonicalPath: path,
    locale: 'es',
    alternates: buildAlternates(path, undefined),
    noindex: d.noindex || d.draft || false,
    ogImage: d.ogImage ?? DEFAULT_OG_IMAGE,
    ogType: collection === 'blog' ? 'article' : 'website',
    datePublished: d.datePublished,
    dateModified: d.dateModified,
    ...extra,
  };
}

// ─────────────────────────────────────────────────────────────────────────
// Sitemap inventory — the same data that feeds <head> feeds the sitemap.
// ─────────────────────────────────────────────────────────────────────────

export interface SitemapEntry {
  path: string;
  lastmod?: Date;
  alternates: Alternate[];
}

export async function getAllIndexablePages(): Promise<SitemapEntry[]> {
  const pages: SitemapEntry[] = [];

  // One-off pages via the paginas collection (noindex/draft excluded)
  const paginas = await getCollection('paginas', (e) => !e.data.noindex && !e.data.draft);
  // Empty-state gates for hubs
  const proyectos = await getCollection('proyectos', (e) => !e.data.draft);
  const posts = await getCollection('blog', (e) => !e.data.draft);
  const reviews = await getCollection('reviews');

  for (const p of paginas) {
    const key = p.data.pageKey;
    if (key === 'proyectos-hub' && !proyectosIndexable(proyectos)) continue;
    if (key === 'blog-hub' && !blogIndexable(posts)) continue;
    if (key === 'opiniones' && reviews.length < 3) continue;
    const locale = entryLocale(p.id);
    const r = staticRoute(key);
    const path = locale === 'en' ? r.en : r.es;
    if (!path) continue;
    pages.push({ path, lastmod: p.data.dateModified, alternates: getStaticAlternates(key) });
  }

  for (const collection of ['servicios', 'precios'] as const) {
    const entries = await getCollection(collection, (e: any) => !e.data.noindex && !e.data.draft);
    for (const e of entries) {
      pages.push({
        path: collectionPath(collection, e),
        lastmod: e.data.dateModified,
        alternates: await getAlternates(collection, e.data.translationKey),
      });
    }
  }

  // Zones: only those passing the quality gate
  const zonas = await getCollection('zonas');
  for (const z of zonas.filter(zonaPassesGate)) {
    const path = collectionPath('zonas', z);
    pages.push({ path, lastmod: z.data.dateModified, alternates: buildAlternates(path) });
  }

  for (const p of proyectos.filter((p) => !p.data.noindex)) {
    const path = collectionPath('proyectos', p);
    pages.push({ path, lastmod: p.data.dateModified, alternates: buildAlternates(path) });
  }

  for (const b of posts.filter((b) => !b.data.noindex)) {
    const path = collectionPath('blog', b);
    pages.push({ path, lastmod: b.data.dateModified, alternates: buildAlternates(path) });
  }

  return pages;
}
