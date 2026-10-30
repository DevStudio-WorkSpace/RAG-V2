import type { HealthInfo, SearchResult, ApiResult } from "./types";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status?: number
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function healthCheck(): Promise<{
  data: HealthInfo | null;
  error: string | null;
}> {
  try {
    const resp = await fetch("/api/health", {
      cache: "no-store",
      signal: AbortSignal.timeout(5000),
    });
    if (!resp.ok) {
      return { data: null, error: `HTTP ${resp.status}` };
    }
    return { data: await resp.json(), error: null };
  } catch (err) {
    return {
      data: null,
      error: err instanceof Error ? err.message : "Error de red",
    };
  }
}

export async function searchImage(
  file: File,
  modelo: string = "fusion"
): Promise<{ data: SearchResult | null; error: string | null }> {
  // Validación cliente: tipo y tamaño ANTES de enviar (evita viajes inútiles)
  if (!file.type.startsWith("image/")) {
    return {
      data: null,
      error: "El archivo no es una imagen válida (JPG, PNG o WEBP).",
    };
  }
  if (file.size === 0) {
    return { data: null, error: "El archivo está vacío." };
  }
  if (file.size > 15 * 1024 * 1024) {
    return {
      data: null,
      error: "La imagen supera el máximo de 15 MB.",
    };
  }

  const fd = new FormData();
  fd.append("file", file);
  fd.append("modo", "auto");
  fd.append("modelo", modelo);

  let resp: Response;
  try {
    resp = await fetch("/api/search", {
      method: "POST",
      body: fd,
      // CLIP en CPU puede tardar: nada de timeouts agresivos de 2.5s.
      signal: AbortSignal.timeout(180_000),
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "TimeoutError") {
      return {
        data: null,
        error:
          "La API tardó más de 3 minutos en responder. Verificá que el proxy /api/search y la API estén activos.",
      };
    }
    return {
      data: null,
      error:
        "No se pudo conectar con el proxy de búsqueda. Verificá que el frontend y la API estén levantados.",
    };
  }

  if (!resp.ok) {
    let detalle = `HTTP ${resp.status}`;
    try {
      const body = await resp.json();
      if (body?.error) detalle = String(body.error);
      else if (body?.detail) detalle = String(body.detail);
    } catch {
      // respuesta no-JNA: mantener detalle genérico
    }
    return { data: null, error: detalle };
  }

  try {
    const json = (await resp.json()) as SearchResult;
    if (!Array.isArray(json.resultados)) {
      return { data: null, error: "La API devolvió una respuesta inesperada." };
    }
    return { data: json, error: null };
  } catch {
    return { data: null, error: "La API devolvió una respuesta ilegible." };
  }
}

export function imageUrl(imagen: string | undefined | null): string | null {
  // La API devuelve el nombre de archivo puro (ej. "AIM-P001-001.jpg").
  // El proxy /api/images/[filename] lo resuelve desde data/images_normalized.
  if (!imagen) return null;
  const limpio = imagen.trim();
  if (!limpio) return null;
  if (limpio.startsWith("http://") || limpio.startsWith("https://")) {
    return limpio; // URL absoluta externa
  }
  return `/api/images/${encodeURIComponent(limpio)}`;
}

export type { ApiResult };
