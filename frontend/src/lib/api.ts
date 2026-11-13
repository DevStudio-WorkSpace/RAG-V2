import type { HealthInfo, SearchResult, ApiResult } from "./types";

// El despliegue objetivo no tiene GPU y la colección Qdrant solo admite CLIP.
export const DEFAULT_SEARCH_MODEL = "clip";

/**
 * Margen de seguridad del cliente por encima del timeout del proxy
 * (`SEARCH_TIMEOUT_MS`, 180 s por defecto). Así el mensaje que ve el usuario
 * es el del proxy, que conoce el presupuesto real configurado.
 */
const CLIENT_SEARCH_TIMEOUT_MS = 190_000;

export type SearchErrorKind =
  | "timeout"
  | "network"
  | "http"
  | "validation"
  | "response";

export interface SearchError {
  message: string;
  kind: SearchErrorKind;
}

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
  modelo: string = DEFAULT_SEARCH_MODEL
): Promise<{ data: SearchResult | null; error: SearchError | null }> {
  // Validación cliente: tipo y tamaño ANTES de enviar (evita viajes inútiles)
  if (!file.type.startsWith("image/")) {
    return {
      data: null,
      error: {
        message: "El archivo no es una imagen válida (JPG, PNG o WEBP).",
        kind: "validation",
      },
    };
  }
  if (file.size === 0) {
    return {
      data: null,
      error: { message: "El archivo está vacío.", kind: "validation" },
    };
  }
  if (file.size > 15 * 1024 * 1024) {
    return {
      data: null,
      error: { message: "La imagen supera el máximo de 15 MB.", kind: "validation" },
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
      signal: AbortSignal.timeout(CLIENT_SEARCH_TIMEOUT_MS),
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "TimeoutError") {
      return {
        data: null,
        error: {
          message:
            "La búsqueda superó el tiempo máximo de espera. Verificá que el proxy /api/search y la API estén activos.",
          kind: "timeout",
        },
      };
    }
    return {
      data: null,
      error: {
        message:
          "No se pudo conectar con el proxy de búsqueda. Verificá que el frontend y la API estén levantados.",
        kind: "network",
      },
    };
  }

  if (!resp.ok) {
    let detalle = `HTTP ${resp.status}`;
    let kind: SearchErrorKind = "http";
    try {
      const body = await resp.json();
      if (body?.error) detalle = String(body.error);
      else if (body?.detail) detalle = String(body.detail);
      if (body?.code === "timeout") kind = "timeout";
      else if (body?.code === "upstream_unreachable") kind = "network";
    } catch {
      // respuesta no-JSON: mantener detalle genérico
    }
    return { data: null, error: { message: detalle, kind } };
  }

  try {
    const json = (await resp.json()) as SearchResult;
    if (!Array.isArray(json.resultados)) {
      return {
        data: null,
        error: {
          message: "La API devolvió una respuesta inesperada.",
          kind: "response",
        },
      };
    }
    return { data: json, error: null };
  } catch {
    return {
      data: null,
      error: {
        message: "La API devolvió una respuesta ilegible.",
        kind: "response",
      },
    };
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
