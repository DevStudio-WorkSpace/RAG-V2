import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function apiUrl(): string {
  return (process.env.API_URL || "http://localhost:8000").replace(/\/+$/, "");
}

export async function GET() {
  let upstream: Response;
  try {
    upstream = await fetch(`${apiUrl()}/health`, {
      cache: "no-store",
      signal: AbortSignal.timeout(5_000),
    });
  } catch {
    return NextResponse.json(
      { error: "No se pudo conectar con la API desde el proxy del frontend." },
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
