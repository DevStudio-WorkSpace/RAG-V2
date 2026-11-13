import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const DEFAULT_TIMEOUT_MS = 180_000;
const MIN_TIMEOUT_MS = 500;

function apiUrl(): string {
  return (process.env.API_URL || "http://localhost:8000").replace(/\/+$/, "");
}

/** Presupuesto de espera del proxy hacia la API (configurable por entorno). */
function searchTimeoutMs(): number {
  const raw = Number(process.env.SEARCH_TIMEOUT_MS);
  if (!Number.isFinite(raw) || raw < MIN_TIMEOUT_MS) return DEFAULT_TIMEOUT_MS;
  return Math.floor(raw);
}

function timeoutMessage(ms: number): string {
  const human =
    ms >= 60_000
      ? `${Math.round(ms / 60_000)} minuto${Math.round(ms / 60_000) === 1 ? "" : "s"}`
      : `${Math.round(ms / 1000)} segundo${Math.round(ms / 1000) === 1 ? "" : "s"}`;
  return `La búsqueda superó el tiempo máximo de espera (${human}) y se canceló. La API no respondió a tiempo.`;
}

export async function POST(request: Request) {
  const clientKey = process.env.API_CLIENT_KEY?.trim();
  if (!clientKey) {
    return NextResponse.json(
      { error: "API_CLIENT_KEY no configurada en el servidor del frontend." },
      { status: 503 }
    );
  }

  let formData: FormData;
  try {
    formData = await request.formData();
  } catch {
    return NextResponse.json(
      { error: "El cuerpo de la petición no es un formulario válido." },
      { status: 400 }
    );
  }

  const upstreamData = new FormData();
  for (const [key, value] of formData.entries()) {
    upstreamData.append(key, value);
  }

  const timeoutMs = searchTimeoutMs();
  let upstream: Response;
  try {
    upstream = await fetch(`${apiUrl()}/search/image`, {
      method: "POST",
      headers: { "X-API-Key": clientKey },
      body: upstreamData,
      cache: "no-store",
      signal: AbortSignal.timeout(timeoutMs),
    });
  } catch (err) {
    const timeout =
      err instanceof DOMException &&
      (err.name === "TimeoutError" || err.name === "AbortError");
    if (timeout) {
      return NextResponse.json(
        { error: timeoutMessage(timeoutMs), code: "timeout" },
        { status: 504 }
      );
    }
    return NextResponse.json(
      {
        error: "No se pudo conectar con la API desde el proxy del frontend.",
        code: "upstream_unreachable",
      },
      { status: 502 }
    );
  }

  const body = await upstream.text();
  return new NextResponse(body, {
    status: upstream.status,
    headers: {
      "Content-Type":
        upstream.headers.get("content-type") || "application/json",
      "Cache-Control": "no-store",
    },
  });
}
