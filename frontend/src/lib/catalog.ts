export interface CatalogJersey {
  id: string;
  name: string;
  team: string;
  country: string;
  league: string;
  season: string;
  collection: "Catálogo Oficial";
  type: "Standard";
  colors: string[];
  colorHexes: string[];
  image: string;
  description: string;
  priceRetail: null;
  priceTeam: null;
  priceLeague: null;
  turnaround: "A consultar";
  fit: "A medida";
  sublimationSpecs: {
    fabric: string;
    collar: string;
    sleeve: string;
    printType: string;
  };
  sampleQueryId?: string;
  url?: string;
}

export interface ProductoCatalogo {
  id: string;
  nombre: string;
  imagen: string;
  url: string;
  proveedor: string;
}

export function toCatalogJersey(producto: ProductoCatalogo): CatalogJersey {
  const id = producto.id.trim();
  const nombre = producto.nombre.trim();
  const imagen = producto.imagen.trim();

  return {
    id,
    name: nombre && nombre !== id ? nombre : `Camiseta Sublitex ${id}`,
    team: "Atelier Sublitex",
    country: "Personalizable",
    league: "Confección a medida",
    season: "Bajo pedido",
    collection: "Catálogo Oficial",
    type: "Standard",
    colors: ["Personalizable"],
    colorHexes: ["#C5A880"],
    image: `/api/images/${encodeURIComponent(imagen)}`,
    description:
      "Modelo del catálogo oficial. Confección en sublimación a medida con tejidos técnicos. Cotización según cantidad, tallas y acabados.",
    priceRetail: null,
    priceTeam: null,
    priceLeague: null,
    turnaround: "A consultar",
    fit: "A medida",
    sublimationSpecs: {
      fabric: "Tejido técnico sublimable (a definir)",
      collar: "A elegir según modelo",
      sleeve: "A elegir según modelo",
      printType: "Sublimación digital UltraHD",
    },
    sampleQueryId: id,
    url: producto.url.trim() || undefined,
  };
}
