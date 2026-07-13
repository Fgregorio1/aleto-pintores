/**
 * Canonical business record — mirrors /NAP.md (the single source of truth).
 * If anything changes: update NAP.md FIRST, then this file, then re-audit
 * every citation (docs/02 §8). Never write NAP values anywhere else in code.
 */

export const SITE_URL = 'https://aletopintores.com';

export const BUSINESS = {
  name: 'Aleto Pintores',
  legalName: 'Paola Alejandra Vera Zambrano',
  taxId: '48473949T',
  url: SITE_URL,
  /** schema.org @id — the entity anchor every Service/WebPage points at */
  id: `${SITE_URL}/#business`,
  phoneDisplay: '624 04 62 10',
  phoneE164: '+34624046210',
  email: 'contacto@aletopintores.com',
  address: {
    street: 'C. de Juan de Austria, 13',
    district: 'Chamberí',
    postalCode: '28010',
    city: 'Madrid',
    region: 'Comunidad de Madrid',
    countryCode: 'ES',
    countryName: 'España',
  },
  /** Display line exactly as in NAP.md */
  addressDisplay: 'C. de Juan de Austria, 13, Chamberí, 28010 Madrid, España',
  foundingYear: 2026,
  hoursDisplay: {
    es: 'Atención 24 h · todos los días',
    en: 'Open 24/7 · every day',
  },
  /** Metro-belt service area (playbook §4, GBP service area) */
  areaServed: [
    'Madrid',
    'Alcorcón',
    'Móstoles',
    'Getafe',
    'Leganés',
    'Fuenlabrada',
    'Las Rozas',
    'Pozuelo de Alarcón',
    'Majadahonda',
    'Alcobendas',
    'San Sebastián de los Reyes',
    'Rivas-Vaciamadrid',
  ],
  /**
   * Entity-resolution glue (docs/02 §4). ADD every real profile the moment
   * it exists (GBP, Instagram, Habitissimo, Houzz…). Never list a profile
   * that hasn't been created — broken sameAs corrodes the entity.
   * GBP uses the stable ?cid= form (never a search/share URL with tokens).
   */
  sameAs: [
    'https://maps.google.com/?cid=17828868560601819322',
    'https://www.instagram.com/aleto.pintores/',
    'https://www.yelp.es/user_details?userid=7k_Gj6Hy2GuOsPZkYi-iwQ',
    'https://www.cronoshare.com/croner-5556442-aleto-pintores',
  ] as string[],
  /** Canonical Google Business Profile link (also first entry of sameAs) */
  gbpUrl: 'https://maps.google.com/?cid=17828868560601819322',
  knowsAbout: [
    'pintura interior',
    'quitar gotelé',
    'alisado de paredes',
    'lacado de puertas',
    'pintura de fachadas',
    'pintura de comunidades',
    'pintura de oficinas',
    'quitar papel pintado',
    'impermeabilización de terrazas',
  ],
} as const;

/**
 * Founder record — the entity behind the business (docs/02 §7: visible
 * name + bio + schema Person must always match; never name someone in
 * JSON-LD who isn't shown on the page).
 * sameAs: add real personal profiles (LinkedIn…) the moment they exist.
 */
export const FOUNDER = {
  name: 'Felipe Gregorio',
  jobTitle: { es: 'Fundador', en: 'Founder' },
  bio: {
    es: 'Tras 7 años dirigiendo una empresa de pintura residencial y comercial en Estados Unidos, fundó Aleto en 2026 para traer ese estándar de servicio a Madrid, trabajando con pintores locales experimentados.',
    en: 'After 7 years running a residential and commercial painting company in the US, he founded Aleto in 2026 to bring that standard of service to Madrid, working with experienced local painters.',
  },
  sameAs: [] as string[],
} as const;

/**
 * Wistia media ID for the presentation video in the contact section.
 * Empty string → a branded placeholder card renders instead of the player.
 * Paste the ID (e.g. "fq4z5flmd8") when the Aleto video exists.
 */
export const WISTIA_MEDIA_ID = '';

/** Keyless Google Maps embed + link (no API key needed) */
const MAPS_QUERY = encodeURIComponent(`${BUSINESS.address.street}, ${BUSINESS.address.postalCode} ${BUSINESS.address.city}`);
export const MAPS_EMBED_URL = `https://maps.google.com/maps?q=${MAPS_QUERY}&output=embed&hl=es`;
export const MAPS_LINK = `https://maps.google.com/?q=${MAPS_QUERY}`;

/** Honest stats for the contact section (no invented client counts) */
export const STATS = [
  { value: '24 h', label: { es: 'Presupuesto cerrado', en: 'Fixed quote' } },
  { value: '2026', label: { es: 'Fundada en Madrid', en: 'Founded in Madrid' } },
  { value: '24/7', label: { es: 'Atención', en: 'Availability' } },
] as const;

/** WhatsApp deep link with optional prefilled message */
export function whatsappLink(message?: string): string {
  const base = `https://wa.me/${BUSINESS.phoneE164.replace('+', '')}`;
  return message ? `${base}?text=${encodeURIComponent(message)}` : base;
}

export const WHATSAPP_DEFAULT_MSG = {
  es: 'Hola, me gustaría pedir un presupuesto de pintura.',
  en: 'Hi, I would like to request a painting quote.',
} as const;
