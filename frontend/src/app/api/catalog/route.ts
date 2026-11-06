import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function csvCandidates(): string[] {
  return [
    process.env.CATALOG_CSV_PATH,
    path.join(process.cwd(), "data", "products.csv"),
    path.join(process.cwd(), "..", "data", "products.csv"),
    path.join("/data", "products.csv"),
  ].filter((value): value is string => Boolean(value));
}

function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = "";
  let quoted = false;

  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];

    if (quoted) {
      if (char === '"') {
        if (text[i + 1] === '"') {
          field += '"';
          i += 1;
        } else {
          quoted = false;
        }
      } else {
        field += char;
      }
      continue;
    }

    if (char === '"') {
      quoted = true;
    } else if (char === ",") {
      row.push(field);
      field = "";
    } else if (char === "\n") {
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
    } else if (char !== "\r") {
      field += char;
    }
  }

  if (field.length > 0 || row.length > 0) {
    row.push(field);
    rows.push(row);
  }

  return rows;
}

export async function GET() {
  const csvPath = csvCandidates().find((candidate) => fs.existsSync(candidate));

  if (!csvPath) {
    return NextResponse.json(
      { error: "No se encontró data/products.csv." },
      { status: 500 }
    );
  }

  const raw = fs.readFileSync(csvPath, "utf8").replace(/^\uFEFF/, "");
  const rows = parseCsv(raw);
  const header = rows.shift()?.map((value) => value.trim()) ?? [];

  const index = {
    id: header.indexOf("id"),
    nombre: header.indexOf("nombre_original"),
    imagen: header.indexOf("imagen"),
    url: header.indexOf("url"),
    proveedor: header.indexOf("proveedor"),
  };

  if (Object.values(index).some((value) => value < 0)) {
    return NextResponse.json(
      { error: "data/products.csv no tiene las columnas requeridas." },
      { status: 500 }
    );
  }

  const productos = rows
    .filter((row) => row[index.id]?.trim())
    .map((row) => ({
      id: row[index.id].trim(),
      nombre: row[index.nombre]?.trim() ?? "",
      imagen: row[index.imagen]?.trim() ?? "",
      url: row[index.url]?.trim() ?? "",
      proveedor: row[index.proveedor]?.trim() ?? "",
    }))
    .filter((producto) => producto.imagen);

  return NextResponse.json(
    { productos },
    { headers: { "Cache-Control": "no-store" } }
  );
}
