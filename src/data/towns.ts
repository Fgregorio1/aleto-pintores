/**
 * Town landing pages for the Google Ads Zona keywords (2026-07-19 CRO
 * rebuild — Wolf "Areas We Serve" pattern). One entry per geo-targeted
 * municipality; Madrid capital is the home page itself.
 *
 * Copy rules: honest and generic — we serve these towns (true: campaign
 * geo-targets them, free visit covers all of them). NEVER claim completed
 * local projects here until real ones exist.
 */
export interface Town {
  slug: string;
  name: string;
  /** natural phrase with preposition, e.g. "en Alcorcón" */
  en: string;
  intro: string;
  barrios: string[];
}

export const TOWNS: Town[] = [
  {
    slug: 'alcorcon',
    name: 'Alcorcón',
    en: 'en Alcorcón',
    intro: 'Pintores profesionales para pisos y casas en Alcorcón, con visita gratuita y presupuesto cerrado en 24 horas.',
    barrios: ['Centro', 'Parque Lisboa', 'Parque Oeste', 'Ensanche Sur'],
  },
  {
    slug: 'mostoles',
    name: 'Móstoles',
    en: 'en Móstoles',
    intro: 'Pintura interior, gotelé y lacado en Móstoles con protección total y fechas por contrato.',
    barrios: ['Centro', 'Villafontana', 'Estoril', 'Parque Coimbra'],
  },
  {
    slug: 'getafe',
    name: 'Getafe',
    en: 'en Getafe',
    intro: 'Tu piso en Getafe pintado en días, no en semanas — el mismo equipo del primer al último día.',
    barrios: ['Centro', 'El Bercial', 'Getafe Norte', 'Sector III'],
  },
  {
    slug: 'leganes',
    name: 'Leganés',
    en: 'en Leganés',
    intro: 'Pintores en Leganés con presupuesto cerrado por escrito y garantía en cada trabajo.',
    barrios: ['Centro', 'Zarzaquemada', 'Valdepelayos', 'Arroyo Culebro'],
  },
  {
    slug: 'fuenlabrada',
    name: 'Fuenlabrada',
    en: 'en Fuenlabrada',
    intro: 'Pintura de pisos y locales en Fuenlabrada, sin polvo y sin que tengas que mudarte.',
    barrios: ['Centro', 'El Arroyo', 'Loranca', 'Parque Miraflores'],
  },
  {
    slug: 'alcobendas',
    name: 'Alcobendas',
    en: 'en Alcobendas',
    intro: 'Acabados finos para pisos y chalets en Alcobendas: preparación a conciencia y entrega revisada a contraluz.',
    barrios: ['Centro', 'La Moraleja', 'Arroyo de la Vega', 'Valdelasfuentes'],
  },
  {
    slug: 'san-sebastian-de-los-reyes',
    name: 'San Sebastián de los Reyes',
    en: 'en San Sebastián de los Reyes',
    intro: 'Pintores en Sanse con visita gratuita, precio cerrado en 24 h y fechas que se cumplen.',
    barrios: ['Centro', 'Dehesa Vieja', 'Tempranales', 'Moscatelares'],
  },
  {
    slug: 'las-rozas',
    name: 'Las Rozas',
    en: 'en Las Rozas',
    intro: 'Pintura interior y lacado de puertas en Las Rozas, con protección total de tu vivienda.',
    barrios: ['Centro', 'Las Matas', 'Monterrozas', 'El Cantizal'],
  },
  {
    slug: 'majadahonda',
    name: 'Majadahonda',
    en: 'en Majadahonda',
    intro: 'Acabados de calidad para pisos y chalets en Majadahonda — oficio traído de 7 años en EE.UU.',
    barrios: ['Centro', 'El Plantío', 'Golf', 'Roza Martín'],
  },
  {
    slug: 'pozuelo-de-alarcon',
    name: 'Pozuelo de Alarcón',
    en: 'en Pozuelo de Alarcón',
    intro: 'Pintores para viviendas exigentes en Pozuelo: muestras de color reales, plazos firmados y repaso pared a pared.',
    barrios: ['Pozuelo pueblo', 'Somosaguas', 'La Finca', 'Húmera'],
  },
  {
    slug: 'boadilla-del-monte',
    name: 'Boadilla del Monte',
    en: 'en Boadilla del Monte',
    intro: 'Pintura interior y exterior en Boadilla con presupuesto cerrado y garantía por escrito.',
    barrios: ['Casco antiguo', 'Las Lomas', 'Valdepastores', 'Olivar de Mirabal'],
  },
  {
    slug: 'rivas-vaciamadrid',
    name: 'Rivas-Vaciamadrid',
    en: 'en Rivas-Vaciamadrid',
    intro: 'Tu casa en Rivas pintada con protección total y limpieza cada tarde — habitable todos los días.',
    barrios: ['Rivas Centro', 'Covibar', 'Rivas Oeste', 'La Luna'],
  },
  {
    slug: 'tres-cantos',
    name: 'Tres Cantos',
    en: 'en Tres Cantos',
    intro: 'Pintores en Tres Cantos con visita gratuita, precio cerrado en 24 horas y fechas por contrato.',
    barrios: ['Centro', 'Sector Océanos', 'Sector Literatos', 'Nuevo Tres Cantos'],
  },
];
