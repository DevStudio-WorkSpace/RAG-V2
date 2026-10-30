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
  "SBX-01-0011.jpg","SBX-01-0012.jpg","SBX-01-0013.jpg","SBX-01-0014.jpg","SBX-01-0015.jpg","SBX-01-0018.jpg","SBX-01-0019.jpg","SBX-01-0020.jpg","SBX-01-0021.jpg","SBX-01-0022.jpg",
  "SBX-01-0023.jpg","SBX-01-0024.jpg","SBX-01-0025.jpg","SBX-01-0026.jpg","SBX-01-0027.jpg","SBX-01-0028.jpg","SBX-01-0029.jpg","SBX-01-0030.jpg","SBX-01-0031.jpg","SBX-01-0032.jpg",
  "SBX-01-0033.jpg","SBX-01-0034.jpg","SBX-01-0035.jpg","SBX-01-0036.jpg","SBX-01-0037.jpg","SBX-01-0038.jpg","SBX-01-0039.jpg","SBX-01-0040.jpg","SBX-01-0041.jpg","SBX-01-0042.jpg",
  "SBX-01-0043.jpg","SBX-01-0044.jpg","SBX-01-0045.jpg","SBX-01-0046.jpg","SBX-01-0048.jpg","SBX-01-0051.jpg","SBX-01-0052.jpg","SBX-01-0053.jpg",
  "SBX-02-0001.jpg","SBX-02-0002.jpg","SBX-02-0003.jpg","SBX-02-0004.jpg","SBX-02-0005.jpg","SBX-02-0006.jpg","SBX-02-0007.jpg","SBX-02-0008.jpg","SBX-02-0009.jpg","SBX-02-0010.jpg",
  "SBX-02-0011.jpg","SBX-02-0013.jpg","SBX-02-0014.jpg","SBX-02-0015.jpg","SBX-02-0016.jpg","SBX-02-0017.jpg","SBX-02-0018.jpg","SBX-02-0019.jpg","SBX-02-0020.jpg","SBX-02-0021.jpg",
  "SBX-02-0022.jpg","SBX-02-0023.jpg","SBX-02-0024.jpg","SBX-02-0025.jpg","SBX-02-0026.jpg","SBX-02-0027.jpg","SBX-02-0028.jpg","SBX-02-0029.jpg","SBX-02-0030.jpg","SBX-02-0031.jpg",
  "SBX-02-0032.jpg","SBX-02-0033.jpg","SBX-02-0034.jpg","SBX-02-0035.jpg","SBX-02-0036.jpg","SBX-02-0037.jpg","SBX-02-0038.jpg","SBX-02-0039.jpg","SBX-02-0040.jpg","SBX-02-0041.jpg",
  "SBX-02-0042.jpg","SBX-02-0043.jpg","SBX-02-0044.jpg","SBX-02-0045.jpg","SBX-02-0046.jpg","SBX-02-0047.jpg","SBX-02-0048.jpg","SBX-02-0050.jpg","SBX-02-0051.jpg","SBX-02-0052.jpg",
  "SBX-02-0053.jpg","SBX-02-0054.jpg","SBX-02-0055.jpg","SBX-02-0056.jpg","SBX-02-0057.jpg","SBX-02-0058.jpg","SBX-02-0059.jpg","SBX-02-0060.jpg","SBX-02-0061.jpg","SBX-02-0062.jpg",
  "SBX-02-0063.jpg","SBX-02-0064.jpg","SBX-02-0065.jpg","SBX-02-0066.jpg","SBX-02-0067.jpg","SBX-02-0068.jpg","SBX-02-0069.jpg","SBX-02-0070.jpg","SBX-02-0071.jpg","SBX-02-0072.jpg",
  "SBX-02-0073.jpg","SBX-02-0074.jpg","SBX-02-0075.jpg","SBX-02-0076.jpg","SBX-02-0077.jpg","SBX-02-0078.jpg","SBX-02-0079.jpg","SBX-02-0080.jpg","SBX-02-0081.jpg","SBX-02-0082.jpg",
  "SBX-02-0083.jpg","SBX-02-0084.jpg","SBX-02-0085.jpg","SBX-02-0086.jpg","SBX-02-0087.jpg","SBX-02-0088.jpg","SBX-02-0089.jpg","SBX-02-0090.jpg","SBX-02-0091.jpg","SBX-02-0092.jpg",
  "SBX-02-0093.jpg","SBX-02-0094.jpg","SBX-02-0095.jpg","SBX-02-0096.jpg","SBX-02-0097.jpg","SBX-02-0098.jpg","SBX-02-0099.jpg","SBX-02-0100.jpg","SBX-02-0101.jpg","SBX-02-0102.jpg",
  "SBX-02-0103.jpg","SBX-02-0104.jpg","SBX-02-0105.jpg","SBX-02-0106.jpg","SBX-02-0107.jpg","SBX-02-0108.jpg","SBX-02-0109.jpg","SBX-02-0110.jpg","SBX-02-0111.jpg","SBX-02-0112.jpg",
  "SBX-02-0113.jpg","SBX-02-0114.jpg","SBX-02-0115.jpg","SBX-02-0116.jpg","SBX-02-0117.jpg","SBX-02-0118.jpg","SBX-02-0119.jpg","SBX-02-0120.jpg","SBX-02-0121.jpg","SBX-02-0122.jpg",
  "SBX-02-0123.jpg","SBX-02-0124.jpg","SBX-02-0125.jpg","SBX-02-0126.jpg","SBX-02-0128.jpg","SBX-02-0129.jpg","SBX-02-0130.jpg","SBX-02-0131.jpg","SBX-02-0132.jpg","SBX-02-0133.jpg",
  "SBX-02-0134.jpg","SBX-02-0135.jpg","SBX-02-0136.jpg","SBX-02-0137.jpg","SBX-02-0138.jpg","SBX-02-0139.jpg","SBX-02-0140.jpg","SBX-02-0141.jpg","SBX-02-0142.jpg","SBX-02-0143.jpg",
  "SBX-02-0144.jpg","SBX-02-0145.jpg","SBX-02-0146.jpg","SBX-02-0147.jpg","SBX-02-0148.jpg","SBX-02-0149.jpg","SBX-02-0150.jpg","SBX-02-0151.jpg","SBX-02-0152.jpg","SBX-02-0153.jpg",
  "SBX-02-0154.jpg","SBX-02-0155.jpg","SBX-02-0156.jpg","SBX-02-0157.jpg","SBX-02-0158.jpg","SBX-02-0159.jpg","SBX-02-0160.jpg","SBX-02-0161.jpg","SBX-02-0162.jpg","SBX-02-0163.jpg",
  "SBX-02-0164.jpg","SBX-02-0165.jpg","SBX-02-0166.jpg","SBX-02-0167.jpg","SBX-02-0168.jpg","SBX-02-0169.jpg","SBX-02-0170.jpg",
  "SBX-04-0001.jpg","SBX-04-0003.jpg","SBX-04-0004.jpg","SBX-04-0005.jpg","SBX-04-0006.jpg","SBX-04-0007.jpg","SBX-04-0008.jpg","SBX-04-0009.jpg","SBX-04-0010.jpg","SBX-04-0011.jpg",
  "SBX-04-0012.jpg","SBX-04-0013.jpg","SBX-04-0014.jpg","SBX-04-0015.jpg","SBX-04-0016.jpg","SBX-04-0017.jpg","SBX-04-0018.jpg","SBX-04-0019.jpg","SBX-04-0020.jpg","SBX-04-0021.jpg",
  "SBX-04-0022.jpg","SBX-04-0023.jpg","SBX-04-0024.jpg","SBX-04-0025.jpg","SBX-04-0026.jpg","SBX-04-0027.jpg","SBX-04-0028.jpg","SBX-04-0029.jpg","SBX-04-0030.jpg","SBX-04-0031.jpg",
  "SBX-04-0032.jpg","SBX-04-0033.jpg","SBX-04-0034.jpg","SBX-04-0035.jpg","SBX-04-0036.jpg","SBX-04-0037.jpg","SBX-04-0038.jpg","SBX-04-0039.jpg","SBX-04-0040.jpg",
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
