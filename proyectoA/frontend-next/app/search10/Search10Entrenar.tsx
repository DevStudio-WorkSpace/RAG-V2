"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import ModelSelect, { MODELO_DEFAULT, ModelKey, modeloDetalle } from "../components/ModelSelect";
import "./search10.css";

const API_URL = "http://localhost:8400";

const IMAGES_URL = `${API_URL}/search10/images`;

function fullUrl(u: string): string {
  if (u.startsWith("http://") || u.startsWith("https://")) return u;
  return `${API_URL}${u}`;
}

type QueryImage = {
  nombre: string;
  url: string;
};

type ResultItem = {
  id: string;
  nombre: string;
  imagen?: string;
  url?: string;
  proveedor?: string;
  score?: number;
  score_reranking?: number;
  posicion_final?: number;
};

type Juicio = "acierto" | "sirve" | "incorrecto";

const JUICIOS: { value: Juicio; label: string; icon: string }[] = [
  { value: "acierto", label: "Correcto", icon: "✅" },
  { value: "sirve", label: "Sirve", icon: "👍" },
  { value: "incorrecto", label: "Incorrecto", icon: "❌" },
];

function toResultImage(result: ResultItem): string {
  if (result.url) return result.url;
  if (result.imagen) {
    const base = result.imagen.trim();
    if (base.startsWith("http://") || base.startsWith("https://")) return base;
    return `${IMAGES_URL}/${encodeURIComponent(base)}`;
  }
  return "";
}

export default function Search10Entrenar() {
  const [imagenes, setImagenes] = useState<QueryImage[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [results, setResults] = useState<ResultItem[]>([]);
  const [feedback, setFeedback] = useState<Record<string, Record<string, Juicio>>>({});
  const [excluidosAplicados, setExcluidosAplicados] = useState<string[]>([]);
  const [poolCandidatos, setPoolCandidatos] = useState(0);
  const [tiempo, setTiempo] = useState<number | null>(null);
  const [buscarEn, setBuscarEn] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [guardandoId, setGuardandoId] = useState<string | null>(null);
  const [modelo, setModelo] = useState<ModelKey>(MODELO_DEFAULT);

  const cargarFeedback = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/search10/feedback`);
      if (!res.ok) throw new Error("No se pudo leer el feedback.");
      const data = await res.json();
      setFeedback(data?.feedback || {});
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo leer el feedback.");
    }
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_URL}/search10/imagenes`);
        if (!res.ok) throw new Error("No se pudo listar proyectoA/Search-10.");
        const data = await res.json();
        setImagenes(Array.isArray(data?.imagenes) ? data.imagenes : []);
      } catch (err) {
        setError(err instanceof Error ? err.message : "No se pudo listar las consultas.");
      }
    })();
    cargarFeedback();
  }, [cargarFeedback]);

  const buscar = useCallback(
    async (nombre: string) => {
      setSelected(nombre);
      setError(null);
      setBuscarEn(true);
      setLoading(true);
      try {
        const res = await fetch(`${API_URL}/search10/buscar`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ imagen: nombre, modelo, top_k: 5 }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data?.error || "La API respondió con error.");
        setResults(Array.isArray(data?.resultados) ? data.resultados : []);
        setExcluidosAplicados(Array.isArray(data.excluidos_aplicados) ? data.excluidos_aplicados : []);
        setPoolCandidatos(data.pool_candidatos ?? 0);
        setTiempo(data.tiempo_segundos ?? null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "No se pudo buscar.");
        setResults([]);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const juicioDe = (r: ResultItem) => (selected ? feedback[selected]?.[r.id] : "");

  const guardarJuicio = async (result: ResultItem, juicio: Juicio) => {
    if (!selected || guardandoId === result.id) return;
    setGuardandoId(result.id);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/search10/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ imagen: selected, id_resultado: result.id, juicio }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || "No se pudo guardar el juicio.");
      setFeedback((prev) => ({
        ...prev,
        [selected]: {
          ...(prev[selected] || {}),
          [result.id]: juicio,
        },
      }));
      if (juicio === "incorrecto") await buscar(selected);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo guardar el juicio.");
    } finally {
      setGuardandoId(null);
    }
  };

  const limpiarConsulta = async () => {
    if (!selected) return;
    const res = await fetch(`${API_URL}/search10/feedback/limpiar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ imagen: selected }),
    });
    if (!res.ok) return;
    setFeedback((prev) => {
      const copia = { ...prev };
      delete copia[selected];
      return copia;
    });
    setBuscarEn(false);
    setSelected(null);
    setResults([]);
  };

  const limpiarTodo = async () => {
    const res = await fetch(`${API_URL}/search10/feedback/limpiar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ imagen: null }),
    });
    if (!res.ok) return;
    setFeedback({});
    setBuscarEn(false);
    setSelected(null);
    setResults([]);
  };

  const totalJuicios = useMemo(
    () => Object.values(feedback).reduce((n, j) => n + Object.keys(j).length, 0),
    [feedback]
  );

  const filaFeedbackSelected = selected ? feedback[selected] || {} : null;
  const excluidosCount = filaFeedbackSelected
    ? Object.values(filaFeedbackSelected).filter((j) => j === "incorrecto").length
    : 0;

  return (
    <div className="app-frame">
      <header className="topbar">
        <div>
          <p className="eyebrow">Search-10 · Entrenamiento</p>
          <h1>Ranking real con retroalimentación</h1>
        </div>
        <div className="topbar-actions">
          <ModelSelect value={modelo} onChange={setModelo} />
          <div className="status-box">
            <span className="status-dot" />
            {totalJuicios === 0
              ? "Sin feedback guardado"
              : `${totalJuicios} juicios persistidos`}
          </div>
        </div>
      </header>

      <section className="s10-layout">
        <aside className="s10-side">
          <div className="s10-side-head">
            <div>
              <p className="label-title">Consultas</p>
              <h3>proyectoA/Search-10</h3>
            </div>
            <span className="results-badge">{imagenes.length}</span>
          </div>
          <p className="s10-hint">
            Agrega o cambia imágenes en la carpeta y presiona
            actualizar. Cada archivo es una consulta de entrenamiento.
          </p>
          {error && <div className="error-box">{error}</div>}

          <div className="s10-query-grid">
            {imagenes.map((img) => {
              const activa = selected === img.nombre;
              const tieneFeedback = !!feedback[img.nombre];
              const nExcl = feedback[img.nombre]
                ? Object.values(feedback[img.nombre]).filter((j) => j === "incorrecto").length
                : 0;
              return (
                <button
                  key={img.nombre}
                  className={`s10-quer card ${activa ? "active" : ""}`}
                  onClick={() => buscar(img.nombre)}
                  title={img.nombre}
                >
                  <img src={fullUrl(img.url)} alt={img.nombre} />
                  <span className="s10-quer-name">{img.nombre}</span>
                  {tieneFeedback && (
                    <span className={`s10-quer-dot ${nExcl > 0 ? "bad" : "ok"}`}>
                      {nExcl > 0 ? `${nExcl} excluidos` : "con feedback"}
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          <div className="s10-side-actions">
            <button className="s10-btn ghost" onClick={() => cargarFeedback()}>
              ↻ Actualizar feedback
            </button>
            <button className="s10-btn danger" onClick={limpiarTodo}>
              Limpiar TODO el feedback
            </button>
          </div>
        </aside>

        <section className="s10-results">
          {!buscarEn ? (
            <div className="empty-state s10-empty">
              Elige una imagen de consulta (izquierda) para ver su ranking
              real y calificar cada resultado.
            </div>
          ) : (
            <>
              <div className="results-header">
                <div>
                  <p className="label-title">Resultados</p>
                  <h3>Top 5 · {selected}</h3>
                </div>
                <span className={`results-badge ${loading ? "loading" : ""}`}>
                  {loading && <span className="spinner" aria-hidden="true" />}
                  {loading ? "Procesando" : "OK"}
                </span>
              </div>

              <div className="s10-meta-row">
                <p className="s10-meta">
                  Modelo: <b>{modeloDetalle(modelo).label}</b> · {modeloDetalle(modelo).detail}
                </p>
                {excluidosCount > 0 && (
                  <p className="hidden-note">
                    ❌ Excluidos por feedback previo para <b>{selected}</b>:{" "}
                    {excluidosCount} resultado{excluidosCount === 1 ? "" : "s"}.
                  </p>
                )}
                {poolCandidatos > 0 && (
                  <p className="s10-meta">
                    Pool de candidatos revisado: {poolCandidatos} ·{" "}
                    {tiempo !== null ? `${tiempo} s` : ""}
                  </p>
                )}
              </div>

              {loading && (
                <div className="progress-track" aria-hidden="true">
                  <div className="progress-bar" />
                </div>
              )}

              <div className="results-grid">
                {results.length > 0 ? (
                  results.map((result, index) => {
                    const score = result.score_reranking ?? result.score ?? 0;
                    const ratio = Math.min(Math.max(score * 100, 0), 100);
                    const juicio = juicioDe(result);
                    return (
                      <article
                        className={`result-card s10-card ${
                          juicio === "acierto" ? "is-correct" : ""
                        } ${juicio === "incorrecto" ? "is-wrong" : ""}`}
                        key={`${result.id}-${index}`}
                      >
                        <div className="card-image-wrap">
                          <span className={`rank-pill ${index === 0 ? "rank-top" : ""}`}>
                            #{result.posicion_final || index + 1}
                          </span>
                          <img src={toResultImage(result)} alt={result.nombre || result.id} />
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
                            {JUICIOS.map((j) => (
                              <button
                                key={j.value}
                                className={`veredicto-btn v-${j.value} ${
                                  juicio === j.value ? "selected" : ""
                                }`}
                                disabled={guardandoId === result.id}
                                onClick={() => guardarJuicio(result, j.value)}
                              >
                                {j.icon} {j.label}
                              </button>
                            ))}
                          </div>
                        </div>
                      </article>
                    );
                  })
                ) : (
                  <div className="empty-state">
                    {excluidosAplicados.length > 0
                      ? "Todos los candidatos de esta consulta fueron excluidos por feedback. Limpia el feedback o revisa Search-10."
                      : "El motor no encontró candidatos visualmente válidos para esta consulta."}
                  </div>
                )}
              </div>

              {filaFeedbackSelected && Object.keys(filaFeedbackSelected).length > 0 && (
                <div className="s10-feedback-state">
                  <p className="label-title">Feedback guardado para {selected}</p>
                  <div className="s10-fb-tags">
                    {Object.entries(filaFeedbackSelected).map(([id, j]) => (
                      <span key={id} className={`s10-fb-tag fb-${j}`}>
                        {id} → {j === "acierto" ? "✅ Correcto" : j === "sirve" ? "👍 Sirve" : "❌ Incorrecto"}
                      </span>
                    ))}
                  </div>
                  <button className="s10-btn danger" onClick={limpiarConsulta}>
                    Borrar feedback de esta consulta
                  </button>
                </div>
              )}
            </>
          )}
        </section>
      </section>
    </div>
  );
}