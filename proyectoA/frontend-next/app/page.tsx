"use client";

import { ChangeEvent, useEffect, useMemo, useState } from "react";
import ModelSelect, { MODELO_DEFAULT, ModelKey, modeloDetalle } from "./components/ModelSelect";

const CASE_TOTAL = 10;
const API_URL = "http://localhost:8000";
const VEREDICTOS_KEY = "buscador_veredictos";

type ResultItem = {
  id: string;
  nombre: string;
  imagen?: string;
  url?: string;
  proveedor?: string;
  score?: number;
  score_reranking?: number;
};

type Veredicto = "acierto" | "sirve" | "no_sirve";

const VEREDICTOS = [
  { value: "acierto", label: "Acierto", icon: "✅" },
  { value: "sirve", label: "Sirve", icon: "👍" },
  { value: "no_sirve", label: "No sirve", icon: "❌" },
] as const;

function buildFallbackImage(text: string, hue = 210) {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800">
      <defs>
        <linearGradient id="g" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="hsl(${hue} 80% 60%)"/>
          <stop offset="100%" stop-color="hsl(${hue + 40} 75% 35%)"/>
        </linearGradient>
      </defs>
      <rect width="800" height="800" fill="url(#g)"/>
      <circle cx="400" cy="250" r="140" fill="rgba(255,255,255,0.25)"/>
      <path d="M220 540 L580 540 L500 280 L300 280 Z" fill="rgba(8,18,30,0.42)"/>
      <text x="50%" y="72%" text-anchor="middle" font-family="Arial, sans-serif" font-size="52" font-weight="700" fill="white" letter-spacing="1">${text}</text>
    </svg>
  `;

  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}

function toResultImage(result: ResultItem, index: number) {
  if (result.url) return result.url;
  if (result.imagen) {
    const base = result.imagen.trim();
    if (base.startsWith("http://") || base.startsWith("https://")) return base;
    return `${API_URL}/images/${encodeURIComponent(base)}`;
  }

  return buildFallbackImage(`#${index + 1}`, 200 + index * 25);
}

function leerVeredictosGuardados(): Record<string, Veredicto> {
  try {
    const raw = localStorage.getItem(VEREDICTOS_KEY);
    return raw ? (JSON.parse(raw) as Record<string, Veredicto>) : {};
  } catch {
    return {};
  }
}

export default function Home() {
  const [queryImage, setQueryImage] = useState<string | null>(null);
  const [queryName, setQueryName] = useState("consulta.png");
  const [results, setResults] = useState<ResultItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("Sin búsqueda");
  const [queryId, setQueryId] = useState<string>("");
  const [modelo, setModelo] = useState<ModelKey>(MODELO_DEFAULT);
  const [veredictos, setVeredictos] = useState<Record<string, Veredicto>>(leerVeredictosGuardados);
  const [guardandoId, setGuardandoId] = useState<string | null>(null);

  useEffect(() => {
    const cargarVeredictos = async () => {
      try {
        const res = await fetch(`${API_URL}/evaluacion/veredictos`);
        if (!res.ok) return;
        const data = await res.json();
        const v = (data?.veredictos || {}) as Record<string, Veredicto>;
        setVeredictos(v);
        localStorage.setItem(VEREDICTOS_KEY, JSON.stringify(v));
      } catch {
        // Sin conexión con la API: se usa lo guardado en localStorage.
      }
    };
    cargarVeredictos();
  }, []);

  const notificarVeredictos = (proximo: Record<string, Veredicto>) => {
    setVeredictos(proximo);
    localStorage.setItem(VEREDICTOS_KEY, JSON.stringify(proximo));
  };

  const guardarVeredicto = async (result: ResultItem, index: number, juicio: Veredicto) => {
    if (guardandoId === result.id) return;

    const previo = veredictos[result.id];
    setGuardandoId(result.id);
    setError(null);
    notificarVeredictos({ ...veredictos, [result.id]: juicio });

    try {
      const res = await fetch(`${API_URL}/evaluacion/guardar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          caso: queryId || "web",
          id_correcto: "",
          posicion: index + 1,
          id_resultado: result.id,
          score: result.score_reranking ?? result.score ?? 0,
          juicio,
          quien: "web",
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data?.detail || "No se pudo guardar el veredicto.");
      }
    } catch (err) {
      setVeredictos((v) => {
        const copia = { ...v };
        if (previo === undefined) {
          delete copia[result.id];
        } else {
          copia[result.id] = previo;
        }
        localStorage.setItem(VEREDICTOS_KEY, JSON.stringify(copia));
        return copia;
      });
      setError(err instanceof Error ? err.message : "No se pudo guardar el veredicto.");
    } finally {
      setGuardandoId(null);
    }
  };

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const objectUrl = URL.createObjectURL(file);
    setQueryImage(objectUrl);
    setQueryName(file.name);
    setLoading(true);
    setError(null);
    setStatus("Buscando coincidencias...");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("modo", "auto");
    formData.append("modelo", modelo);

    try {
      const response = await fetch(`${API_URL}/search/image`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.error || "La API respondió con error.");
      }

      const nextResults = Array.isArray(data?.resultados) ? data.resultados : [];
      setResults(nextResults);
      if (data?.query_id) setQueryId(data.query_id);
      const usado = modeloDetalle((data?.modelo as string) || modelo).label;
      setStatus(`Top 5 · ${usado}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo buscar.");
      setResults([]);
      setStatus("Fallo de conexión");
    } finally {
      setLoading(false);
    }
  };

  const ocultas = useMemo(
    () => results.filter((r) => veredictos[r.id] === "no_sirve").length,
    [results, veredictos]
  );
  const topResults = useMemo(
    () => results.filter((r) => veredictos[r.id] !== "no_sirve").slice(0, 5),
    [results, veredictos]
  );

  return (
    <main className="page-shell">
      <div className="app-frame">
        <header className="topbar">
          <div>
            <p className="eyebrow">Búsqueda visual</p>
            <h1>Encuentra camisetas visualmente similares</h1>
          </div>
          <div className="status-box">
            <span className="status-dot" />
            {status}
          </div>
        </header>

        <section className="upload-panel">
          <div className="upload-header">
            <div>
              <p className="label-title">Consulta</p>
              <h2>Sube una imagen de camiseta</h2>
            </div>
            <label className="upload-button" htmlFor="file-upload">
              {loading ? "Buscando..." : "Elegir imagen"}
            </label>
            <input id="file-upload" type="file" accept="image/*" onChange={handleFileChange} />
          </div>

          <div className="case-row">
            <div className="case-badge">Caso 1 de {CASE_TOTAL}</div>
            <div className="meta-inline">
              <span>Modo</span>
              <strong>auto</strong>
              <span>•</span>
              <ModelSelect value={modelo} onChange={setModelo} />
            </div>
          </div>

          <div className="query-panel">
            {queryImage ? (
              <img src={queryImage} alt={queryName} className="query-image" />
            ) : (
              <div className="query-placeholder">
                <div className="placeholder-icon">🧢</div>
                <p>Vista previa de la imagen de consulta</p>
              </div>
            )}
          </div>
        </section>

        <section className="results-panel">
          <div className="results-header">
            <div>
              <p className="label-title">Resultados</p>
              <h3>Top 5 más parecidos</h3>
            </div>
            <span className={`results-badge ${loading ? "loading" : ""}`}>
              {loading && <span className="spinner" aria-hidden="true" />}
              {loading ? "Procesando" : "OK"}
            </span>
          </div>

          {loading && (
            <div className="progress-track" aria-hidden="true">
              <div className="progress-bar" />
            </div>
          )}

          {error ? (
            <div className="error-box">{error}</div>
          ) : null}

          {ocultas > 0 && (
            <p className="hidden-note">
              Se ocultaron {ocultas} imagen{ocultas === 1 ? "" : "es"} marcada{ocultas === 1 ? "" : "s"} como No sirve.
            </p>
          )}

          <div className="results-grid">
            {topResults.length > 0 ? (
              topResults.map((result, index) => {
                const score = result.score_reranking ?? result.score ?? 0;
                const ratio = Math.min(Math.max(score * 100, 0), 100);
                const imageSrc = toResultImage(result, index);
                const seleccionado = veredictos[result.id];

                return (
                  <article className="result-card" key={`${result.id}-${index}`}>
                    <div className="card-image-wrap">
                      <span className={`rank-pill ${index === 0 ? "rank-top" : ""}`}>
                        #{index + 1}
                      </span>
                      <img src={imageSrc} alt={result.nombre || result.id} />
                    </div>

                    <div className="card-body">
                      <h4>{result.nombre || result.id}</h4>
                      <p className="product-meta">
                        {result.id} · {result.proveedor || "Designs Aimari"}
                      </p>

                      <div className="score-block">
                        <div className="score-label-row">
                          <span>Score</span>
                          <strong>{Number(score || 0).toFixed(2)}</strong>
                        </div>
                        <div className="score-bar">
                          <span style={{ width: `${ratio}%` }} />
                        </div>
                      </div>

                      <div className="veredicto-buttons">
                        {VEREDICTOS.map((v) => (
                          <button
                            key={v.value}
                            className={`veredicto-btn v-${v.value} ${seleccionado === v.value ? "selected" : ""}`}
                            disabled={guardandoId === result.id}
                            onClick={() => guardarVeredicto(result, index, v.value)}
                          >
                            {v.icon} {v.label}
                          </button>
                        ))}
                      </div>
                    </div>
                  </article>
                );
              })
            ) : (
              <div className="empty-state">
                {results.length > 0
                  ? "Todas las imágenes de esta búsqueda fueron marcadas como No sirve."
                  : "Sube una imagen para consultar la API y ver los resultados realistas del Top 5."}
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}