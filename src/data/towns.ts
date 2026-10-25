/**
 * Town landing pages for the Google Ads Zona keywords (2026-07-19 CRO
 * rebuild — Wolf "Areas We Serve" pattern). One entry per geo-targeted
 * municipality of Gran Bilbao; Bilbao capital is the home page itself.
 * (Replaced the Madrid metro-belt list on 2026-10-25 — old slugs 301 to /.)
 *
 * Copy rules: honest and generic — we serve these towns (true: the free
 * visit covers all of them). NEVER claim completed
 * local projects here until real ones exist.
 */
export interface Town {
  slug: string;
  name: string;
  /** natural phrase with preposition, e.g. "en Barakaldo" */
  en: string;
  intro: string;
  /** Only well-known barrios; may be empty (page falls back to a generic line) */
  barrios: string[];
}

export const TOWNS: Town[] = [
  {
    slug: 'barakaldo',
    name: 'Barakaldo',
    en: 'en Barakaldo',
    intro: 'Pintores profesionales para pisos y casas en Barakaldo, con visita gratuita y presupuesto cerrado en 24 horas.',
    barrios: ['Centro', 'Cruces', 'Retuerto', 'Rontegi'],
  },
  {
    slug: 'getxo',
    name: 'Getxo',
    en: 'en Getxo',
    intro: 'Acabados finos para pisos y chalets en Getxo: preparación a conciencia y entrega revisada a contraluz.',
    barrios: ['Algorta', 'Las Arenas', 'Neguri', 'Romo'],
  },
  {
    slug: 'portugalete',
    name: 'Portugalete',
    en: 'en Portugalete',
    intro: 'Pintura interior, gotelé y lacado en Portugalete con protección total y fechas por contrato.',
    barrios: ['Casco Viejo', 'Abatxolo', 'Repélega'],
  },
  {
    slug: 'santurtzi',
    name: 'Santurtzi',
    en: 'en Santurtzi',
    intro: 'Tu piso en Santurtzi pintado en días, no en semanas — el mismo equipo del primer al último día.',
    barrios: ['Centro', 'Mamariga', 'Kabiezes'],
  },
  {
    slug: 'basauri',
    name: 'Basauri',
    en: 'en Basauri',
    intro: 'Pintores en Basauri con presupuesto cerrado por escrito y garantía en cada trabajo.',
    barrios: ['San Miguel', 'Ariz', 'Basozelai', 'Pozokoetxe'],
  },
  {
    slug: 'leioa',
    name: 'Leioa',
    en: 'en Leioa',
    intro: 'Pintura de pisos y locales en Leioa, sin polvo y sin que tengas que mudarte.',
    barrios: ['Centro', 'Lamiako', 'Ondiz'],
  },
  {
    slug: 'galdakao',
    name: 'Galdakao',
    en: 'en Galdakao',
    intro: 'Pintura interior y exterior en Galdakao con presupuesto cerrado y garantía por escrito.',
    barrios: ['Centro', 'Bengoetxe', 'Aperribai'],
  },
  {
    slug: 'sestao',
    name: 'Sestao',
    en: 'en Sestao',
    intro: 'Pintores en Sestao con visita gratuita, precio cerrado en 24 h y fechas que se cumplen.',
    barrios: ['Centro', 'Kueto', 'Txabarri', 'Urbinaga'],
  },
  {
    slug: 'erandio',
    name: 'Erandio',
    en: 'en Erandio',
    intro: 'Pintura interior y lacado de puertas en Erandio, con protección total de tu vivienda.',
    barrios: ['Altzaga', 'Astrabudua', 'Asua'],
  },
  {
    slug: 'sopela',
    name: 'Sopela',
    en: 'en Sopela',
    intro: 'Pintores para pisos y casas en Sopela: muestras de color reales, plazos firmados y repaso pared a pared.',
    barrios: ['Centro', 'Larrabasterra'],
  },
  {
    slug: 'arrigorriaga',
    name: 'Arrigorriaga',
    en: 'en Arrigorriaga',
    intro: 'Tu casa en Arrigorriaga pintada con protección total y limpieza cada tarde — habitable todos los días.',
    barrios: [],
  },
  {
    slug: 'etxebarri',
    name: 'Etxebarri',
    en: 'en Etxebarri',
    intro: 'Pintores en Etxebarri con visita gratuita, precio cerrado en 24 horas y fechas por contrato.',
    barrios: [],
  },
];
