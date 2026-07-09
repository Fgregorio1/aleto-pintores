import type { CollectionEntry } from 'astro:content';

/**
 * QUALITY GATES (docs/02 §5) — the difference between programmatic SEO
 * and a doorway-page penalty. A zone page earns the right to exist only
 * when there is real local proof behind it. Enforced in getStaticPaths
 * (page not built) AND re-checked by the sitemap.
 */

/** A zone page builds only with ≥1 real project OR ≥2 zone reviews, plus filled substance fields. */
export function zonaPassesGate(zona: CollectionEntry<'zonas'>): boolean {
  const d = zona.data;
  const hasProof = d.proyectos.length >= 1 || d.reviews.length >= 2;
  const hasSubstance = d.vivienda.trim().length >= 80 && d.notas_precio.trim().length >= 40;
  return hasProof && hasSubstance;
}

/** The gallery index is only indexable once real projects exist. */
export function proyectosIndexable(proyectos: CollectionEntry<'proyectos'>[]): boolean {
  return proyectos.filter((p) => !p.data.draft).length >= 1;
}

/** The reviews page is only indexable once real reviews exist. */
export function opinionesIndexable(reviews: CollectionEntry<'reviews'>[]): boolean {
  return reviews.length >= 3;
}

/** The blog index is only indexable once posts exist. */
export function blogIndexable(posts: CollectionEntry<'blog'>[]): boolean {
  return posts.filter((p) => !p.data.draft).length >= 1;
}
