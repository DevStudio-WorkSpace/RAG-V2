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
}

function makeName(id: string): string {
  const num = id.replace("SBX-", "").replace(/-/g, " ");
  return `Camiseta Sublitex ${id}`;
}

const IMAGES = [
  "SBX-01-0001.jpg","SBX-01-0002.jpg","SBX-01-0003.jpg","SBX-01-0004.jpg","SBX-01-0005.jpg","SBX-01-0006.jpg","SBX-01-0007.jpg","SBX-01-0008.jpg","SBX-01-0009.jpg","SBX-01-0010.jpg",
  "SBX-01-0011.jpg","SBX-01-0012.jpg","SBX-01-0013.jpg","SBX-01-0014.jpg","SBX-01-0015.jpg","SBX-01-0016.jpg","SBX-01-0017.jpg","SBX-01-0018.jpg","SBX-01-0019.jpg","SBX-01-0020.jpg",
  "SBX-01-0021.jpg","SBX-01-0022.jpg","SBX-01-0023.jpg","SBX-01-0024.jpg","SBX-01-0025.jpg","SBX-01-0026.jpg","SBX-01-0027.jpg","SBX-01-0028.jpg","SBX-01-0029.jpg","SBX-01-0030.jpg",
  "SBX-01-0031.jpg","SBX-01-0032.jpg","SBX-01-0033.jpg","SBX-01-0034.jpg","SBX-01-0035.jpg","SBX-01-0036.jpg","SBX-01-0037.jpg","SBX-01-0038.jpg","SBX-01-0039.jpg","SBX-01-0040.jpg",
  "SBX-02-0001.jpg","SBX-02-0002.jpg","SBX-02-0003.jpg","SBX-02-0004.jpg","SBX-02-0005.jpg","SBX-02-0006.jpg","SBX-02-0007.jpg","SBX-02-0008.jpg","SBX-02-0009.jpg","SBX-02-0010.jpg",
  "SBX-02-0011.jpg","SBX-02-0012.jpg","SBX-02-0013.jpg","SBX-02-0014.jpg","SBX-02-0015.jpg","SBX-02-0016.jpg","SBX-02-0017.jpg","SBX-02-0018.jpg","SBX-02-0019.jpg","SBX-02-0020.jpg",
  "SBX-02-0021.jpg","SBX-02-0022.jpg","SBX-02-0023.jpg","SBX-02-0024.jpg","SBX-02-0025.jpg","SBX-02-0026.jpg","SBX-02-0027.jpg","SBX-02-0028.jpg","SBX-02-0029.jpg","SBX-02-0030.jpg",
  "SBX-02-0031.jpg","SBX-02-0032.jpg","SBX-02-0033.jpg","SBX-02-0034.jpg","SBX-02-0035.jpg","SBX-02-0036.jpg","SBX-02-0037.jpg","SBX-02-0038.jpg","SBX-02-0039.jpg","SBX-02-0040.jpg",
  "SBX-03-0001.jpg","SBX-03-0002.jpg","SBX-03-0003.jpg","SBX-03-0004.jpg","SBX-03-0005.jpg","SBX-03-0006.jpg","SBX-03-0007.jpg","SBX-03-0008.jpg","SBX-03-0009.jpg","SBX-03-0010.jpg",
  "SBX-03-0011.jpg","SBX-03-0012.jpg","SBX-03-0013.jpg","SBX-03-0014.jpg","SBX-03-0015.jpg","SBX-03-0016.jpg","SBX-03-0017.jpg","SBX-03-0018.jpg","SBX-03-0019.jpg","SBX-03-0020.jpg",
  "SBX-03-0021.jpg","SBX-03-0022.jpg","SBX-03-0023.jpg","SBX-03-0024.jpg","SBX-03-0025.jpg","SBX-03-0026.jpg","SBX-03-0027.jpg","SBX-03-0028.jpg","SBX-03-0029.jpg","SBX-03-0030.jpg",
  "SBX-03-0031.jpg","SBX-03-0032.jpg","SBX-03-0033.jpg","SBX-03-0034.jpg","SBX-03-0035.jpg","SBX-03-0036.jpg","SBX-03-0037.jpg","SBX-03-0038.jpg","SBX-03-0039.jpg","SBX-03-0040.jpg",
  "SBX-04-0001.jpg","SBX-04-0002.jpg","SBX-04-0003.jpg","SBX-04-0004.jpg","SBX-04-0005.jpg","SBX-04-0006.jpg","SBX-04-0007.jpg","SBX-04-0008.jpg","SBX-04-0009.jpg","SBX-04-0010.jpg",
  "SBX-04-0011.jpg","SBX-04-0012.jpg","SBX-04-0013.jpg","SBX-04-0014.jpg","SBX-04-0015.jpg","SBX-04-0016.jpg","SBX-04-0017.jpg","SBX-04-0018.jpg","SBX-04-0019.jpg","SBX-04-0020.jpg",
  "SBX-04-0021.jpg","SBX-04-0022.jpg","SBX-04-0023.jpg","SBX-04-0024.jpg","SBX-04-0025.jpg","SBX-04-0026.jpg","SBX-04-0027.jpg","SBX-04-0028.jpg","SBX-04-0029.jpg","SBX-04-0030.jpg",
  "SBX-04-0031.jpg","SBX-04-0032.jpg","SBX-04-0033.jpg","SBX-04-0034.jpg","SBX-04-0035.jpg","SBX-04-0036.jpg","SBX-04-0037.jpg","SBX-04-0038.jpg","SBX-04-0039.jpg","SBX-04-0040.jpg",
  "SBX-05-0001.jpg","SBX-05-0002.jpg","SBX-05-0003.jpg","SBX-05-0004.jpg","SBX-05-0005.jpg","SBX-05-0006.jpg","SBX-05-0007.jpg","SBX-05-0008.jpg","SBX-05-0009.jpg","SBX-05-0010.jpg",
  "SBX-05-0011.jpg","SBX-05-0012.jpg","SBX-05-0013.jpg","SBX-05-0014.jpg","SBX-05-0015.jpg","SBX-05-0016.jpg","SBX-05-0017.jpg","SBX-05-0018.jpg","SBX-05-0019.jpg","SBX-05-0020.jpg",
  "SBX-05-0021.jpg","SBX-05-0022.jpg","SBX-05-0023.jpg","SBX-05-0024.jpg","SBX-05-0025.jpg","SBX-05-0026.jpg","SBX-05-0027.jpg","SBX-05-0028.jpg","SBX-05-0029.jpg","SBX-05-0030.jpg",
  "SBX-05-0031.jpg","SBX-05-0032.jpg","SBX-05-0033.jpg","SBX-05-0034.jpg","SBX-05-0035.jpg","SBX-05-0036.jpg","SBX-05-0037.jpg","SBX-05-0038.jpg","SBX-05-0039.jpg","SBX-05-0040.jpg",
];

export const CATALOG_JERSEYS: CatalogJersey[] = IMAGES.map((img) => {
  const id = img.replace(/\.(jpg|jpeg|png|webp)$/i, "");
  return {
    id,
    name: makeName(id),
    team: "Atelier Sublitex",
    country: "Personalizable",
    league: "Confección a medida",
    season: "Bajo pedido",
    collection: "Catálogo Oficial",
    type: "Standard",
    colors: ["Personalizable"],
    colorHexes: ["#C5A880"],
    image: `/api/images/${img}`,
    description: "Modelo del catálogo oficial. Confección en sublimación a medida con tejidos técnicos. Cotización según cantidad, tallas y acabados.",
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
  };
});
