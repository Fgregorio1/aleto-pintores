import type { CollectionEntry } from 'astro:content';

/**
 * Collection entry → canonical URL path.
 * Entry ids include the locale folder: 'es/quitar-gotele-alisar-paredes',
 * 'en/gotele-removal-wall-smoothing'. EN slugs are English-keyword slugs,
 * so ES and EN paths are asymmetric by design.
 */

export function entrySlug(id: string): string {
  return id.replace(/^(es|en)\//, '');
}

export function entryLocale(id: string): 'es' | 'en' {
  return id.startsWith('en/') ? 'en' : 'es';
}

export function servicioPath(entry: CollectionEntry<'servicios'>): string {
  const slug = entrySlug(entry.id);
  return entryLocale(entry.id) === 'en' ? `/en/services/${slug}/` : `/servicios/${slug}/`;
}

export function precioPath(entry: CollectionEntry<'precios'>): string {
  const slug = entrySlug(entry.id);
  return entryLocale(entry.id) === 'en' ? `/en/prices/${slug}/` : `/precios/${slug}/`;
}

export function zonaPath(entry: CollectionEntry<'zonas'>): string {
  return `/pintores/${entry.data.slug}/`;
}

export function proyectoPath(entry: CollectionEntry<'proyectos'>): string {
  return `/proyectos/${entrySlug(entry.id)}/`;
}

export function blogPath(entry: CollectionEntry<'blog'>): string {
  return `/blog/${entrySlug(entry.id)}/`;
}

type PathedCollection = 'servicios' | 'precios' | 'zonas' | 'proyectos' | 'blog';

export function collectionPath(collection: PathedCollection, entry: any): string {
  switch (collection) {
    case 'servicios':
      return servicioPath(entry);
    case 'precios':
      return precioPath(entry);
    case 'zonas':
      return zonaPath(entry);
    case 'proyectos':
      return proyectoPath(entry);
    case 'blog':
      return blogPath(entry);
  }
}
