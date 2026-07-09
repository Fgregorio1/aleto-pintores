import { defineCollection, reference, z } from 'astro:content';
import { glob } from 'astro/loaders';

/**
 * ══════════════════════════════════════════════════════════════════════
 * THE META CONTRACT (docs/03 §2)
 * Every field that ends up in <head> (title, description, dates, FAQ,
 * hreflang pairing) lives HERE, in frontmatter — never in templates.
 * Editing a page's frontmatter is the ONLY way meta changes, so content
 * and meta can never drift apart. Zod limits act as the meta linter:
 * a title over 60 chars or a description outside 70–160 fails the build.
 * ══════════════════════════════════════════════════════════════════════
 */
const seoBase = {
  /** <title> before the brand suffix. ≤60 chars so it never truncates in SERPs. */
  title: z.string().min(15).max(60),
  /** Meta description. 70–160 chars — Google's display window. */
  metaDescription: z.string().min(70).max(160),
  /** Visible H1 — may differ from title (H1 targets the query verbatim). */
  h1: z.string(),
  /** Pairs ES↔EN versions. Same key in both locales = hreflang pair exists. */
  translationKey: z.string(),
  locale: z.enum(['es', 'en']).default('es'),
  /**
   * The 2–3 sentence direct answer with concrete numbers rendered at the
   * top of the page (docs/02 §3). This is what featured snippets and AI
   * assistants lift verbatim.
   */
  directAnswer: z.string().min(80).max(500),
  /** Rendered visibly by <Faq/> AND emitted as FAQPage schema — by construction they can't diverge. */
  faq: z.array(z.object({ q: z.string(), a: z.string() })).default([]),
  datePublished: z.coerce.date(),
  /** Drives visible "Actualizado", schema dateModified and sitemap lastmod. Bump on every content edit. */
  dateModified: z.coerce.date(),
  ogImage: z.string().optional(),
  noindex: z.boolean().default(false),
  draft: z.boolean().default(false),
};

const servicios = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/servicios' }),
  schema: z.object({
    ...seoBase,
    /** schema.org Service name */
    serviceName: z.string(),
    /** Key into src/data/precios.yaml — price table + JSON-LD offers read from there */
    priceKey: z.string(),
    /** Steps shown in the "Cómo trabajamos" section */
    proceso: z.array(z.object({ paso: z.string(), detalle: z.string() })).default([]),
    relatedServices: z.array(reference('servicios')).default([]),
    relatedPrecio: reference('precios').optional(),
    /** Short label for cards/nav */
    shortLabel: z.string(),
    /** One-line summary for service cards */
    excerpt: z.string().max(160),
    /** Sort order in hubs/nav */
    orden: z.number().default(99),
  }),
});

const precios = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/precios' }),
  schema: z.object({
    ...seoBase,
    priceKey: z.string(),
    showCalculator: z.boolean().default(false),
    /** Evidence note: "según nuestros presupuestos de 2026, n=…" (GEO: evidence-dense content gets cited more) */
    metodologia: z.string(),
    relatedServicio: reference('servicios').optional(),
    shortLabel: z.string(),
    excerpt: z.string().max(160),
    orden: z.number().default(99),
  }),
});

/** One-off pages (home, about, contact, hubs, legal). pageKey maps to a route in src/i18n/routes.ts */
const paginas = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/paginas' }),
  schema: z.object({
    ...seoBase,
    pageKey: z.string(),
    // Direct answer is optional on utility pages (contact, legal)
    directAnswer: z.string().min(80).max(500).optional(),
  }),
});

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    ...seoBase,
    /** E-E-A-T: every post is authored by a named person (docs/02 §7) */
    author: z.string(),
    /** Forces "only when it serves a query" — a post must name the search query it answers */
    targetQuery: z.string(),
    excerpt: z.string().max(160),
  }),
});

const proyectos = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/proyectos' }),
  schema: z.object({
    ...seoBase,
    zonaSlug: z.string(),
    servicios: z.array(reference('servicios')).min(1),
    superficieM2: z.number(),
    precioTotal: z.number(),
    duracionDias: z.number(),
    fecha: z.coerce.date(),
    /** min(2) is itself a quality gate: no real photos, no project page */
    imagenes: z
      .array(
        z.object({
          src: z.string(),
          alt: z.string(),
          caption: z.string().optional(),
          fase: z.enum(['antes', 'durante', 'despues']),
        }),
      )
      .min(2),
  }),
});

/**
 * Programmatic zone pages — data model from docs/02 §5.
 * QUALITY GATE (enforced in src/lib/gates.ts): a page only builds with
 * ≥1 real project OR ≥2 zone reviews, plus vivienda + notas_precio filled.
 */
const zonas = defineCollection({
  loader: glob({ pattern: '**/*.yaml', base: './src/data/zonas' }),
  schema: z.object({
    slug: z.string(),
    nombre: z.string(),
    tipo: z.enum(['distrito', 'municipio']),
    poblacion: z.number(),
    /** Housing-stock paragraph — the anti-doorway substance. min(80) forces real content. */
    vivienda: z.string().min(80),
    notas_precio: z.string().min(40),
    precio_pintar_piso_80m2: z.tuple([z.number(), z.number()]),
    barrios: z.array(z.string()).default([]),
    proyectos: z.array(z.string()).default([]),
    reviews: z.array(z.string()).default([]),
    translationKey: z.string(),
    dateModified: z.coerce.date(),
  }),
});

const reviews = defineCollection({
  loader: glob({ pattern: '**/*.yaml', base: './src/data/reviews' }),
  schema: z.object({
    id: z.string(),
    autor: z.string(),
    zonaSlug: z.string().optional(),
    servicioKey: z.string().optional(),
    rating: z.number().min(1).max(5),
    texto: z.string(),
    fecha: z.coerce.date(),
    fuente: z.enum(['google', 'habitissimo', 'houzz', 'directa']),
  }),
});

export const collections = { servicios, precios, paginas, blog, proyectos, zonas, reviews };
