import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function apiUrl(): string {
  return (process.env.API_URL || "http://localhost:8000").replace(/\/+$/, "");
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

  let upstream: Response;
  try {
    upstream = await fetch(`${apiUrl()}/search/image`, {
      method: "POST",
      headers: { "X-API-Key": clientKey },
      body: upstreamData,
      cache: "no-store",
      signal: AbortSignal.timeout(180_000),
    });
  } catch (err) {
    const timeout =
      err instanceof DOMException && err.name === "TimeoutError";
    return NextResponse.json(
      {
        error: timeout
          ? "La API tardó más de 3 minutos en responder."
          : "No se pudo conectar con la API desde el proxy del frontend.",
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
