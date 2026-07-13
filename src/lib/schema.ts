import type { CollectionEntry } from 'astro:content';
import { BUSINESS, FOUNDER, SITE_URL } from '@/data/business';
import preciosData from '@/data/precios.yaml';
import { absolute, type SEOData } from './seo';

/**
 * JSON-LD builders (docs/02 §4). One site-wide HousePainter node anchored at
 * @id "#business"; every per-page node references it — that's the
 * entity-resolution glue AI models and Google use to connect the site,
 * GBP and directories into one entity.
 *
 * RULES: FAQPage only for FAQs visibly on the page (guaranteed: built from
 * the same frontmatter the <Faq/> component renders). No aggregateRating
 * until genuine first-party reviews are displayed on-page.
 */

export function businessSchema(): object {
  return {
    '@context': 'https://schema.org',
    '@type': 'HousePainter',
    '@id': BUSINESS.id,
    name: BUSINESS.name,
    legalName: BUSINESS.legalName,
    taxID: BUSINESS.taxId,
    url: BUSINESS.url,
    telephone: BUSINESS.phoneE164,
    email: BUSINESS.email,
    image: absolute('/img/og-default.jpg'),
    logo: absolute('/img/og-default.jpg'),
    priceRange: '€€',
    foundingDate: String(BUSINESS.foundingYear),
    address: {
      '@type': 'PostalAddress',
      streetAddress: BUSINESS.address.street,
      addressLocality: BUSINESS.address.city,
      postalCode: BUSINESS.address.postalCode,
      addressRegion: BUSINESS.address.region,
      addressCountry: BUSINESS.address.countryCode,
    },
    areaServed: BUSINESS.areaServed.map((name) => ({ '@type': 'City', name })),
    openingHoursSpecification: [
      {
        '@type': 'OpeningHoursSpecification',
        dayOfWeek: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        opens: '00:00',
        closes: '23:59',
      },
    ],
    ...(BUSINESS.sameAs.length > 0 ? { sameAs: BUSINESS.sameAs } : {}),
    knowsAbout: BUSINESS.knowsAbout,
    // Reciprocal entity link: business→founder here, founder→business via
    // worksFor in founderSchema(). Same @id so the nodes merge.
    founder: { '@type': 'Person', '@id': `${SITE_URL}/#founder`, name: FOUNDER.name },
  };
}

/** Service node with real price ranges pulled from precios.yaml via priceKey. */
export function serviceSchema(entry: CollectionEntry<'servicios'>, canonicalPath: string): object {
  const price = preciosData.servicios[entry.data.priceKey];
  return {
    '@context': 'https://schema.org',
    '@type': 'Service',
    '@id': `${absolute(canonicalPath)}#service`,
    name: entry.data.serviceName,
    serviceType: entry.data.serviceName,
    description: entry.data.metaDescription,
    url: absolute(canonicalPath),
    provider: { '@id': BUSINESS.id },
    areaServed: BUSINESS.areaServed.map((name) => ({ '@type': 'City', name })),
    ...(price
      ? {
          offers: {
            '@type': 'Offer',
            priceCurrency: preciosData.moneda,
            priceSpecification: {
              '@type': 'PriceSpecification',
              minPrice: price.min,
              maxPrice: price.max,
              priceCurrency: preciosData.moneda,
            },
            availability: 'https://schema.org/InStock',
          },
        }
      : {}),
  };
}

export function faqSchema(faq: { q: string; a: string }[]): object | null {
  if (!faq.length) return null;
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faq.map(({ q, a }) => ({
      '@type': 'Question',
      name: q,
      acceptedAnswer: { '@type': 'Answer', text: a },
    })),
  };
}

export interface Crumb {
  name: string;
  path: string;
}

export function breadcrumbSchema(items: Crumb[]): object {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: item.name,
      item: absolute(item.path),
    })),
  };
}

export function webPageSchema(seo: SEOData): object {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    '@id': absolute(seo.canonicalPath),
    url: absolute(seo.canonicalPath),
    name: seo.title,
    description: seo.description,
    inLanguage: seo.locale === 'es' ? 'es-ES' : 'en',
    isPartOf: { '@id': `${SITE_URL}/#website` },
    about: { '@id': BUSINESS.id },
    ...(seo.datePublished ? { datePublished: seo.datePublished.toISOString().slice(0, 10) } : {}),
    ...(seo.dateModified ? { dateModified: seo.dateModified.toISOString().slice(0, 10) } : {}),
  };
}

export function websiteSchema(): object {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    '@id': `${SITE_URL}/#website`,
    url: SITE_URL,
    name: BUSINESS.name,
    publisher: { '@id': BUSINESS.id },
    inLanguage: ['es-ES', 'en'],
  };
}

/**
 * Founder Person node — only rendered on /sobre-nosotros/ + /en/about/
 * (docs/02 §7), where the same name/bio/photo are VISIBLE on the page.
 * Data comes from FOUNDER in business.ts; image is passed in by the page
 * because the optimized asset URL only exists there (astro:assets).
 */
export function founderSchema(locale: 'es' | 'en', imageUrl?: string): object {
  return {
    '@context': 'https://schema.org',
    '@type': 'Person',
    '@id': `${SITE_URL}/#founder`,
    name: FOUNDER.name,
    jobTitle: FOUNDER.jobTitle[locale],
    description: FOUNDER.bio[locale],
    knowsAbout: BUSINESS.knowsAbout,
    ...(imageUrl ? { image: absolute(imageUrl) } : {}),
    ...(FOUNDER.sameAs.length > 0 ? { sameAs: FOUNDER.sameAs } : {}),
    worksFor: { '@id': BUSINESS.id },
  };
}
