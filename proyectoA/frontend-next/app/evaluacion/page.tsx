"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Search10Entrenar from "../search10/Search10Entrenar";
import { MODELO_DEFAULT } from "../components/ModelSelect";
import "./evaluacion.css";

const API_URL = "http://localhost:8000";

type Tab = "evaluador" | "search10";

type ResultItem = {
  id: string;
  nombre?: string;
  imagen?: string;
  url?: string;
  proveedor?: string;
  score?: number;
  score_reranking?: number;
};

type Juicios = Record<string, string>;

type CasoMeta = {
  caso: string;
  archivo: string;
  imagen_url: string;
  id_correcto: string;
  tipo: string;
  juicios: Juicios;
  evaluado: boolean;
};

const JUICIOS = [
  { value: "acierto", label: "Acierto", cls: "j-acierto" },
  { value: "sirve", label: "Sirve", cls: "j-sirve" },
  { value: "no_sirve", label: "No sirve", cls: "j-no-sirve" },
];

function resultImage(result: ResultItem) {
  if (result.url) return result.url;
  if (result.imagen) {
    const base = result.imagen.trim();
    if (base.startsWith("http://") || base.startsWith("https://")) return base;
    return `${API_URL}/images/${encodeURIComponent(base)}`;
  }
  return "";
}

export default function Evaluacion() {
  const [tab, setTab] = useState<Tab>("evaluador");
  const [quien, setQuien] = useState("");
  const [casos, setCasos] = useState<CasoMeta[]>([]);
  const [current, setCurrent] = useState<CasoMeta | null>(null);
  const [results, setResults] = useState<ResultItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [iniciado, setIniciado] = useState(false);

  const cacheRef = useRef<Record<string, ResultItem[]>>({});

  const pending = useMemo(() => casos.filter((c) => !c.evaluado), [casos]);

  const cargarCaso = useCallback(async (meta: CasoMeta) => {
    setCurrent(meta);
    setError(null);

    if (cacheRef.current[meta.caso]) {
      setResults(cacheRef.current[meta.caso]);
      setLoading(false);
      return;
    }

    setLoading(true);
    const formData = new FormData();
    const blob = await fetch(meta.imagen_url).then((r) => r.blob());
    formData.append("file", blob, meta.archivo);
    formData.append("modo", "auto");
    formData.append("modelo", MODELO_DEFAULT);

    try {
      const res = await fetch(`${API_URL}/search/image`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || "La API respondió con error.");

      const nextResults = Array.isArray(data?.resultados)
        ? data.resultados.slice(0, 5)
        : [];
      cacheRef.current[meta.caso] = nextResults;
      setResults(nextResults);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo buscar este caso.");
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const guardado = localStorage.getItem("evaluador_quien");
    if (guardado) setQuien(guardado);

    (async () => {
      try {
        const res = await fetch(`${API_URL}/evaluacion/estado`);
        if (!res.ok) throw new Error("No se pudo leer el estado de evaluación.");
        const data = await res.json();
        const lista: CasoMeta[] = Array.isArray(data?.casos) ? data.casos : [];
        setCasos(lista);
      } catch (err) {
        setError(err instanceof Error ? err.message : "No se pudo leer el estado de evaluación.");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  useEffect(() => {
    if (loading || casos.length === 0 || iniciado || pending.length === 0) return;
    setIniciado(true);
    cargarCaso(pending[0]);
  }, [loading, casos, iniciado, pending, cargarCaso]);

  async function guardarJuicio(posicion: number, resultado: ResultItem, juicio: string) {
    if (!current || !resultado || saving) return;

    setSaving(true);
    setError(null);
    const juiciosPrevios = current.juicios;
    const optimista: Juicios = { ...juiciosPrevios, [String(posicion)]: juicio };
    setCurrent((c) => (c ? { ...c, juicios: optimista } : c));

    try {
      const body = {
        caso: current.caso,
        id_correcto: current.id_correcto,
        posicion,
        id_resultado: resultado.id,
        score: resultado.score_reranking ?? resultado.score ?? 0,
        juicio,
        quien: quien || "anonimo",
      };
      const res = await fetch(`${API_URL}/evaluacion/guardar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data?.detail || "No se pudo guardar el juicio.");
      }

      if (results.length > 0 && Object.keys(optimista).length >= results.length) {
        await completarCaso(current.caso);
        setCasos((prev) =>
          prev.map((c) => (c.caso === current.caso ? { ...c, evaluado: true } : c))
        );
        const siguiente = pending.find((c) => c.caso !== current.caso);
        if (siguiente) cargarCaso(siguiente);
      }
    } catch (err) {
      setCurrent((c) => (c ? { ...c, juicios: juiciosPrevios } : c));
      setError(err instanceof Error ? err.message : "No se pudo guardar el juicio.");
    } finally {
      setSaving(false);
    }
  }

  async function completarCaso(caso: string) {
    const res = await fetch(`${API_URL}/evaluacion/completar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ caso }),
    });
    if (!res.ok) throw new Error("No se pudo marcar el caso como completado.");
  }

  function irAlSiguiente() {
    if (!current) return;
    const pos = pending.findIndex((c) => c.caso === current.caso);
    const siguiente = pending[pos + 1];
    if (siguiente) cargarCaso(siguiente);
  }

  const nroCaso = current ? pending.findIndex((c) => c.caso === current.caso) : 0;
  const nroCasoGlobal = current ? casos.findIndex((c) => c.caso === current.caso) : 0;
  const terminado = !loading && casos.length > 0 && pending.length === 0;

  return (
    <main className="page-shell">
      <div className="app-frame">
        <nav className="eval-tabs" aria-label="Secciones">
          <button
            className={`eval-tab ${tab === "evaluador" ? "active" : ""}`}
            onClick={() => setTab("evaluador")}
          >
            📋 Evaluador
          </button>
          <button
            className={`eval-tab ${tab === "search10" ? "active" : ""}`}
            onClick={() => setTab("search10")}
          >
            🎯 Search-10 · Entrenar
          </button>
        </nav>

        {tab === "search10" ? (
          <Search10Entrenar />
        ) : (
        <>
        <header className="topbar">
          <div>
            <p className="eyebrow">Evaluador del buscador</p>
            <h1>Califica los cinco resultados</h1>
          </div>
          <div className="status-box">
            <span className="status-dot" />
            {terminado
              ? "Evaluación completa"
              : loading
                ? "Cargando..."
                : `${casos.length - pending.length} de ${casos.length} casos`}
          </div>
        </header>

        <section className="eval-bar">
          <label className="quien-field">
            <span>Evaluador/a</span>
            <input
              value={quien}
              onChange={(e) => {
                setQuien(e.target.value);
                localStorage.setItem("evaluador_quien", e.target.value);
              }}
              placeholder="Nombre o iniciales"
            />
          </label>

          <div className="eval-model-badge">
            <span>Modelo fijo</span>
            <strong>Fusión (CLIP + OpenCLIP + SigLIP)</strong>
          </div>

          <div className="legend">
            <span className="legend-item"><b>Acierto</b> es el mismo diseño</span>
            <span className="legend-item"><b>Sirve</b> no es el mismo, pero lo aceptaría un cliente</span>
            <span className="legend-item"><b>No sirve</b> es otro diseño</span>
          </div>
        </section>

        {error ? <div className="error-box">{error}</div> : null}

        {terminado ? (
          <section className="eval-done">
            <h2>¡Los {casos.length} casos ya están evaluados!</h2>
            <p>Las filas quedaron guardadas en <code>evaluador/resultados.csv</code>.</p>
          </section>
        ) : current ? (
          <>
            <section className="eval-query-panel">
              <div className="eval-query-head">
                <div>
                  <p className="label-title">Consulta · {current.tipo}</p>
                  <h2>
                    Caso {nroCasoGlobal + 1} de {casos.length}
                  </h2>
                </div>
                <div className="eval-pill">{current.caso}</div>
              </div>

              <div className="eval-query-grid">
                <div className="query-panel eval-query-img">
                  {loading ? (
                    <div className="query-placeholder">Buscando coincidencias...</div>
                  ) : (
                    <img
                      src={current.imagen_url}
                      alt={current.caso}
                      className="query-image"
                    />
                  )}
                </div>

                <div className="eval-results">
                  {results.length === 0 && !loading ? (
                    <div className="empty-state">Este caso no tiene resultados.</div>
                  ) : (
                    results.map((result, index) => {
                      const pos = index + 1;
                      const yaJuzgado = current.juicios[String(pos)];

                      return (
                        <article className="eval-card" key={`${current.caso}-${result.id}-${index}`}>
                          <span className="rank-pill eval-rank">#{pos}</span>
                          <div className="eval-card-img">
                            {resultImage(result) ? (
                              // eslint-disable-next-line @next/next/no-img-element
                              <img src={resultImage(result)} alt={result.nombre || result.id} />
                            ) : (
                              <div className="eval-card-fallback">{result.nombre || result.id}</div>
                            )}
                          </div>
                          <div className="eval-card-body">
                            <h4>{result.nombre || result.id}</h4>
                            <p className="product-meta">
                              {result.id} · {Number(result.score_reranking ?? result.score ?? 0).toFixed(2)}
                            </p>
                            <div className="juicio-buttons">
                              {JUICIOS.map((j) => (
                                <button
                                  key={j.value}
                                  className={`juicio-btn ${j.cls} ${yaJuzgado === j.value ? "selected" : ""} ${yaJuzgado ? "disabled" : ""}`}
                                  disabled={!!yaJuzgado || saving}
                                  onClick={() => guardarJuicio(pos, result, j.value)}
                                >
                                  {yaJuzgado === j.value ? "✓ " : ""}
                                  {j.label}
                                </button>
                              ))}
                            </div>
                          </div>
                        </article>
                      );
                    })
                  )}
                </div>
              </div>

              <div className="eval-nav">
                <span className="eval-progress">
                  {Object.keys(current.juicios).length}/{results.length || 5} resultados
                </span>
                <button className="next-button" onClick={irAlSiguiente} disabled={nroCaso + 1 >= pending.length}>
                  Siguiente →
                </button>
              </div>
            </section>
          </>
        ) : (
          <section className="empty-state">No hay casos cargados en evaluador/casos/.</section>
        )}
        </>
        )}
      </div>
    </main>
  );
}