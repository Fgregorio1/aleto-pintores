/**
 * Canonical business record — mirrors /NAP.md (the single source of truth).
 * If anything changes: update NAP.md FIRST, then this file, then re-audit
 * every citation (docs/02 §8). Never write NAP values anywhere else in code.
 */

export const SITE_URL = 'https://aletopintores.com';

export const BUSINESS = {
  name: 'Aleto Pintores',
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
   */
  sameAs: [] as string[],
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

/** WhatsApp deep link with optional prefilled message */
export function whatsappLink(message?: string): string {
  const base = `https://wa.me/${BUSINESS.phoneE164.replace('+', '')}`;
  return message ? `${base}?text=${encodeURIComponent(message)}` : base;
}

export const WHATSAPP_DEFAULT_MSG = {
  es: 'Hola, me gustaría pedir un presupuesto de pintura.',
  en: 'Hi, I would like to request a painting quote.',
} as const;
