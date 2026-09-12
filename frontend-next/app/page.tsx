"use client";

import { ChangeEvent, useMemo, useState } from "react";

const CASE_TOTAL = 10;

const demoResults = [
  {
    id: "AIM-P121-007",
    name: "Camiseta Selección Azul",
    provider: "Designs Aimari",
    score: 0.98,
    image:
      "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "AIM-P088-201",
    name: "Camiseta Técnica Rojo",
    provider: "Designs Aimari",
    score: 0.95,
    image:
      "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "AIM-P045-118",
    name: "Jersey Negro Estampado",
    provider: "Designs Aimari",
    score: 0.91,
    image:
      "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "AIM-P302-041",
    name: "Camiseta Verde Fútbol",
    provider: "Designs Aimari",
    score: 0.88,
    image:
      "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "AIM-P219-090",
    name: "Camiseta Blanca con Rayas",
    provider: "Designs Aimari",
    score: 0.84,
    image:
      "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=900&q=80",
  },
];

export default function Home() {
  const [queryImage, setQueryImage] = useState<string | null>(null);
  const [queryName, setQueryName] = useState("consulta.png");

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const nextUrl = URL.createObjectURL(file);
    setQueryImage(nextUrl);
    setQueryName(file.name);
  };

  const topResults = useMemo(() => demoResults, []);

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
            API OK · 1000 productos
          </div>
        </header>

        <section className="upload-panel">
          <div className="upload-header">
            <div>
              <p className="label-title">Consulta</p>
              <h2>Sube una imagen de camiseta</h2>
            </div>
            <label className="upload-button" htmlFor="file-upload">
              Elegir imagen
            </label>
            <input id="file-upload" type="file" accept="image/*" onChange={handleFileChange} />
          </div>

          <div className="case-row">
            <div className="case-badge">Caso 1 de {CASE_TOTAL}</div>
            <div className="meta-inline">
              <span>Modo</span>
              <strong>auto</strong>
              <span>•</span>
              <span>Modelo</span>
              <strong>fusion</strong>
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
            <span className="results-badge">0.9 s</span>
          </div>

          <div className="results-grid">
            {topResults.map((result, index) => (
              <article className="result-card" key={result.id}>
                <div className="card-image-wrap">
                  <span className={`rank-pill ${index === 0 ? "rank-top" : ""}`}>
                    #{index + 1}
                  </span>
                  <img src={result.image} alt={result.name} />
                </div>

                <div className="card-body">
                  <h4>{result.name}</h4>
                  <p className="product-meta">
                    {result.id} · {result.provider}
                  </p>

                  <div className="score-block">
                    <div className="score-label-row">
                      <span>Score</span>
                      <strong>{result.score.toFixed(2)}</strong>
                    </div>
                    <div className="score-bar">
                      <span style={{ width: `${result.score * 100}%` }} />
                    </div>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
