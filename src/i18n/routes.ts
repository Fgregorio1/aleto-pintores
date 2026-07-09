import type { Locale } from './ui';

/**
 * Translation map for NON-collection routes (one-off .astro pages).
 * A pair exists iff both `es` and `en` are set — that's what drives
 * hreflang tags, the language switcher and the sitemap for these pages.
 * Collection pages (servicios/precios/…) pair via `translationKey` instead
 * (see src/lib/seo.ts).
 */
export interface StaticRoute {
  key: string;
  es: string;
  en?: string;
}

export const staticRoutes: StaticRoute[] = [
  { key: 'home', es: '/', en: '/en/' },
  { key: 'servicios-hub', es: '/servicios/', en: '/en/services/' },
  { key: 'precios-hub', es: '/precios/', en: '/en/prices/' },
  { key: 'sobre-nosotros', es: '/sobre-nosotros/', en: '/en/about/' },
  { key: 'contacto', es: '/contacto/', en: '/en/contact/' },
  { key: 'opiniones', es: '/opiniones/' },
  { key: 'proyectos-hub', es: '/proyectos/' },
  { key: 'blog-hub', es: '/blog/' },
  { key: 'aviso-legal', es: '/aviso-legal/' },
  { key: 'politica-privacidad', es: '/politica-privacidad/' },
];

export function staticRoute(key: string): StaticRoute {
  const r = staticRoutes.find((r) => r.key === key);
  if (!r) throw new Error(`Unknown static route key: ${key}`);
  return r;
}

export function staticPath(key: string, locale: Locale): string {
  const r = staticRoute(key);
  const path = locale === 'en' ? r.en : r.es;
  if (!path) throw new Error(`Route "${key}" has no ${locale} version`);
  return path;
}
