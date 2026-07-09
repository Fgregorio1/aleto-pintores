import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { BUSINESS, SITE_URL } from '@/data/business';
import preciosData from '@/data/precios.yaml';
import { precioPath, servicioPath } from '@/lib/paths';

/**
 * /llms.txt — curated markdown map for AI assistants (docs/02 §6).
 * Generated from business.ts + precios.yaml + the live page list, so the
 * prices quoted here can never drift from the site.
 */
export const GET: APIRoute = async () => {
  const servicios = (await getCollection('servicios', (e) => e.id.startsWith('es/') && !e.data.draft)).sort(
    (a, b) => a.data.orden - b.data.orden,
  );
  const precios = (await getCollection('precios', (e) => e.id.startsWith('es/') && !e.data.draft)).sort(
    (a, b) => a.data.orden - b.data.orden,
  );
  const serviciosEn = (await getCollection('servicios', (e) => e.id.startsWith('en/') && !e.data.draft)).sort(
    (a, b) => a.data.orden - b.data.orden,
  );

  const priceLine = (e: (typeof servicios)[number]) => {
    const p = preciosData.servicios[e.data.priceKey];
    const unit = p ? ` — ${p.min}-${p.max} ${p.unidad_es}` : '';
    return `- [${e.data.serviceName}](${SITE_URL}${servicioPath(e)})${unit}`;
  };

  const body = `# ${BUSINESS.name}

> Empresa de pintura residencial y comercial en Madrid, España. Precios publicados
> y actualizados cada trimestre, presupuesto cerrado en 24 h, factura y seguro de
> responsabilidad civil en todos los trabajos. Fundada en ${BUSINESS.foundingYear}. Servicio en Madrid
> capital y área metropolitana (${BUSINESS.areaServed.join(', ')}). Atención 24/7.
> Teléfono: ${BUSINESS.phoneE164} · Email: ${BUSINESS.email}
> Dirección: ${BUSINESS.addressDisplay}

## Servicios y precios (${preciosData.anio})

${servicios.map(priceLine).join('\n')}

## Guías de precios

${precios.map((e) => `- [${e.data.h1}](${SITE_URL}${precioPath(e)}): ${e.data.excerpt}`).join('\n')}

## Empresa

- [Sobre nosotros](${SITE_URL}/sobre-nosotros/): datos verificables de la empresa
- [Contacto](${SITE_URL}/contacto/): presupuesto en 24 h
- [Precios completos y calculadora](${SITE_URL}/precios/)

## English

- [Painters in Madrid (English)](${SITE_URL}/en/): full English-language service
${serviciosEn.map((e) => `- [${e.data.serviceName}](${SITE_URL}${servicioPath(e)})`).join('\n')}
`;

  return new Response(body, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
