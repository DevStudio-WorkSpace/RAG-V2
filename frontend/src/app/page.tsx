"use client";

import { useState, useEffect, useCallback } from "react";

// ────────────────────────────────────────────────────────────
// Types
// ────────────────────────────────────────────────────────────
type EvalCase = {
  id_caso: string;
  descripcion: string;
  id_correcto: string;
  tipo?: string;
};

type ApiResult = {
  id: string;
  nombre: string;
  imagen: string;
  url: string;
  score: number;
  score_reranking?: number;
};

type Rating = "Acierto" | "Sirve" | "No sirve";

type RatedResult = {
  id: string;
  nombre: string;
  imagen: string;
  position: number;
  score: number;
  rating: Rating;
};

type CaseEval = {
  id_caso: string;
  id_correcto: string;
  descripcion: string;
  tipo?: string;
  rated: RatedResult[];
  completed_at: string;
};

type Session = {
  cases: EvalCase[];
  evals: CaseEval[];
  current_idx: number;
};

const LS_KEY = "evaluador_v2_session";

// ────────────────────────────────────────────────────────────
// Metrics  (los tres números que pide la ficha)
// ────────────────────────────────────────────────────────────
function calcMetrics(evals: CaseEval[]) {
  const n = evals.length;
  if (!n) return { p1: 0, r5: 0, util: 0 };

  let p1 = 0, r5 = 0, utilSum = 0, utilN = 0;

  for (const ev of evals) {
    // Precision@1: posición 1 fue "Acierto"
    const top1 = ev.rated.find((r) => r.position === 1);
    if (top1?.rating === "Acierto") p1++;

    // Recall@5: el id_correcto aparece entre los 5 Y fue marcado Acierto
    const found = ev.rated.find(
      (r) => r.id === ev.id_correcto && r.rating === "Acierto"
    );
    if (found) r5++;

    // Utilidad del Top 5: de los no-Acierto, ¿cuántos son "Sirve"?
    const others = ev.rated.filter((r) => r.rating !== "Acierto");
    if (others.length) {
      utilSum +=
        others.filter((r) => r.rating === "Sirve").length / others.length;
      utilN++;
    }
  }

  return {
    p1: Math.round((p1 / n) * 100),
    r5: Math.round((r5 / n) * 100),
    util: utilN ? Math.round((utilSum / utilN) * 100) : 100,
  };
}

// ────────────────────────────────────────────────────────────
// CSV export
// ────────────────────────────────────────────────────────────
function exportCSV(evals: CaseEval[]) {
  const rows = [
    "caso,tipo,descripcion,id_correcto,posicion,id_resultado,nombre,score,juicio",
  ];
  for (const ev of evals) {
    for (const r of ev.rated) {
      rows.push(
        [
          ev.id_caso,
          ev.tipo ?? "",
          `"${ev.descripcion}"`,
          ev.id_correcto,
          r.position,
          r.id,
          `"${r.nombre}"`,
          r.score.toFixed(4),
          r.rating,
        ].join(",")
      );
    }
  }
  const blob = new Blob([rows.join("\n")], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "evaluacion.csv";
  a.click();
  URL.revokeObjectURL(url);
}

// ────────────────────────────────────────────────────────────
// Criteria legend — obligatorio visible en pantalla (Fase 3)
// ────────────────────────────────────────────────────────────
function CriteriaLegend() {
  return (
    <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm">
      <p className="font-bold text-amber-800 uppercase tracking-wider text-xs mb-3">
        Criterios de juicio — fijos, no los decides tú
      </p>
      <div className="space-y-2">
        {[
          {
            label: "Acierto",
            color: "text-emerald-700",
            text: "Es el mismo diseño, aunque cambie el color, el año, el escudo o el sponsor.",
          },
          {
            label: "Sirve",
            color: "text-amber-700",
            text: "No es el mismo, pero se lo mostrarías al cliente y lo aceptaría.",
          },
          {
            label: "No sirve",
            color: "text-rose-700",
            text: "Es otro diseño.",
          },
        ].map((c) => (
          <div key={c.label} className="flex items-start gap-3">
            <span className={`w-20 font-black flex-shrink-0 ${c.color}`}>
              {c.label}
            </span>
            <span className="text-gray-600">{c.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ────────────────────────────────────────────────────────────
// Metric card
// ────────────────────────────────────────────────────────────
function MetricCard({
  label,
  value,
  description,
  gradient,
}: {
  label: string;
  value: number;
  description: string;
  gradient: string;
}) {
  return (
    <div className={`${gradient} rounded-2xl p-6 text-white shadow-lg`}>
      <p className="text-xs font-bold uppercase tracking-widest opacity-80 mb-1">
        {label}
      </p>
      <p className="text-5xl font-black mb-2">{value}%</p>
      <p className="text-xs opacity-70 leading-relaxed">{description}</p>
    </div>
  );
}

// ────────────────────────────────────────────────────────────
// Interpretation row
// ────────────────────────────────────────────────────────────
function InterpretRow({ label, value }: { label: string; value: number }) {
  const s =
    value >= 70
      ? { icon: "✅", text: "Motor listo para los 180 casos", color: "text-emerald-600" }
      : value >= 50
      ? { icon: "⚠️", text: "Aceptable — margen de mejora", color: "text-amber-600" }
      : { icon: "❌", text: "Motor necesita mejoras antes de producción", color: "text-rose-600" };
  return (
    <div className="flex items-center gap-3 text-sm">
      <span>{s.icon}</span>
      <span className="font-bold w-32 text-gray-700">{label}</span>
      <span className={`font-black ${s.color}`}>{value}%</span>
      <span className="text-gray-400">— {s.text}</span>
    </div>
  );
}

// ────────────────────────────────────────────────────────────
// MAIN COMPONENT
// ────────────────────────────────────────────────────────────
export default function Evaluador() {
  const [phase, setPhase] = useState<"setup" | "evaluating" | "done">("setup");
  const [session, setSession] = useState<Session | null>(null);
  const [queryFile, setQueryFile] = useState<File | null>(null);
  const [queryPreview, setQueryPreview] = useState<string | null>(null);
  const [apiResults, setApiResults] = useState<ApiResult[]>([]);
  const [ratings, setRatings] = useState<Record<string, Rating>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  // ── Hydration guard ──
  useEffect(() => {
    setMounted(true);
  }, []);

  // ── Restore from localStorage ──
  useEffect(() => {
    if (!mounted) return;
    try {
      const saved = localStorage.getItem(LS_KEY);
      if (saved) {
        const s: Session = JSON.parse(saved);
        setSession(s);
        if (s.current_idx >= s.cases.length && s.evals.length > 0) {
          setPhase("done");
        } else if (s.cases.length > 0) {
          setPhase("evaluating");
        }
      }
    } catch {}
  }, [mounted]);

  const persist = useCallback((s: Session) => {
    localStorage.setItem(LS_KEY, JSON.stringify(s));
    setSession(s);
  }, []);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  };

  // ── SETUP: load JSON ──
  const handleJsonLoad = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    setError(null);
    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const raw = JSON.parse(ev.target?.result as string);
        const cases: EvalCase[] = raw.cases ?? raw;
        if (
          !Array.isArray(cases) ||
          !cases.length ||
          !cases[0]?.id_correcto
        ) {
          setError(
            'El JSON debe tener: { "cases": [{ "id_caso", "descripcion", "id_correcto", "tipo" }] }'
          );
          return;
        }
        const s: Session = { cases, evals: [], current_idx: 0 };
        persist(s);
        setPhase("evaluating");
        showToast(`✓ ${cases.length} casos cargados`);
      } catch {
        setError("No se pudo leer el JSON. Verifica que sea válido.");
      }
    };
    reader.readAsText(f);
  };

  const resetSession = () => {
    localStorage.removeItem(LS_KEY);
    setSession(null);
    setPhase("setup");
    setQueryFile(null);
    setQueryPreview(null);
    setApiResults([]);
    setRatings({});
    setError(null);
  };

  // ── EVALUATING ──
  const currentCase = session?.cases[session.current_idx] ?? null;

  const handleImageSelect = (file: File) => {
    if (!file.type.startsWith("image/")) {
      setError("Solo se aceptan archivos de imagen.");
      return;
    }
    setQueryFile(file);
    setQueryPreview(URL.createObjectURL(file));
    setApiResults([]);
    setRatings({});
    setError(null);
  };

  const handleSearch = async () => {
    if (!queryFile) return;
    setLoading(true);
    setError(null);
    const fd = new FormData();
    fd.append("file", queryFile);
    fd.append("modo", "auto");
    try {
      const res = await fetch("http://localhost:8000/search/image", {
        method: "POST",
        body: fd,
      });
      if (!res.ok) throw new Error(`API respondió con error ${res.status}`);
      const data = await res.json();
      const docs: ApiResult[] = data.resultados ?? data;
      setApiResults(docs.slice(0, 5));
      showToast("Resultados recibidos ✓");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error desconocido";
      setError(`No se pudo conectar con la API: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRate = (id: string, rating: Rating) => {
    setRatings((prev) => ({ ...prev, [id]: rating }));
  };

  const allRated =
    apiResults.length > 0 && apiResults.every((r) => !!ratings[r.id]);

  const handleNextCase = () => {
    if (!session || !currentCase || !allRated) return;

    const rated: RatedResult[] = apiResults.map((r, i) => ({
      id: r.id,
      nombre: r.nombre,
      imagen: r.imagen,
      position: i + 1,
      score: r.score_reranking ?? r.score ?? 0,
      rating: ratings[r.id] as Rating,
    }));

    const newEval: CaseEval = {
      id_caso: currentCase.id_caso,
      id_correcto: currentCase.id_correcto,
      descripcion: currentCase.descripcion,
      tipo: currentCase.tipo,
      rated,
      completed_at: new Date().toISOString(),
    };

    const newSession: Session = {
      ...session,
      evals: [...session.evals, newEval],
      current_idx: session.current_idx + 1,
    };

    persist(newSession); // ← guarda en localStorage inmediatamente
    setQueryFile(null);
    setQueryPreview(null);
    setApiResults([]);
    setRatings({});

    if (newSession.current_idx >= newSession.cases.length) {
      setPhase("done");
      showToast("¡Evaluación completada! 🎉");
    } else {
      showToast(
        `Caso guardado. Siguiente: ${newSession.cases[newSession.current_idx].id_caso}`
      );
    }
  };

  const metrics = session ? calcMetrics(session.evals) : { p1: 0, r5: 0, util: 0 };

  if (!mounted) return null;

  // ────────────────────────────────────────────────────────
  // RENDER
  // ────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Toast */}
      <div
        className={`fixed bottom-6 right-6 bg-gray-900 text-white px-5 py-3 rounded-xl shadow-2xl z-50 flex items-center gap-2 transition-all duration-300 ${
          toast
            ? "opacity-100 translate-y-0"
            : "opacity-0 translate-y-4 pointer-events-none"
        }`}
      >
        <span className="text-sm font-medium">{toast}</span>
      </div>

      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-40">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-700">
              Evaluador del Buscador
            </h1>
            <p className="text-xs text-gray-400 font-mono">
              Sublitex · Ficha 03-C · Programación
            </p>
          </div>
          {phase !== "setup" && session && (
            <div className="flex items-center gap-4">
              {phase === "evaluating" && (
                <span className="text-sm font-bold text-gray-600">
                  Caso {session.current_idx + 1} / {session.cases.length}
                </span>
              )}
              {phase === "done" && (
                <span className="text-sm font-bold text-emerald-600">
                  ✓ {session.evals.length} casos completados
                </span>
              )}
              <button
                onClick={resetSession}
                className="text-xs text-gray-400 hover:text-red-500 transition-colors border border-gray-200 px-3 py-1 rounded-lg hover:border-red-300"
              >
                Nueva sesión
              </button>
            </div>
          )}
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8 space-y-6">

        {/* ══════════════════════════════════════════════ SETUP */}
        {phase === "setup" && (
          <div className="flex flex-col items-center gap-8">
            <div className="text-center">
              <h2 className="text-3xl font-black text-gray-800 mb-2">
                Cargar casos de prueba
              </h2>
              <p className="text-gray-500 max-w-lg">
                Sube el archivo{" "}
                <code className="bg-gray-100 px-1.5 py-0.5 rounded font-mono text-sm">
                  casos.json
                </code>{" "}
                con tus 10 casos. El progreso se guarda automáticamente en el
                navegador — si cierras y vuelves a abrir, continúas donde
                dejaste.
              </p>
            </div>

            <label className="w-full max-w-lg cursor-pointer bg-white border-2 border-dashed border-blue-200 rounded-2xl p-10 flex flex-col items-center gap-3 hover:border-blue-400 hover:bg-blue-50 transition-all">
              <span className="text-5xl">📂</span>
              <span className="font-bold text-gray-700 text-lg">
                Haz clic para cargar casos.json
              </span>
              <span className="text-sm text-gray-400 text-center">
                {"{ cases: [{ id_caso, descripcion, id_correcto, tipo }] }"}
              </span>
              <input
                type="file"
                accept=".json"
                className="hidden"
                onChange={handleJsonLoad}
              />
            </label>

            {error && (
              <p className="text-red-600 text-sm bg-red-50 px-4 py-3 rounded-xl border border-red-100 max-w-lg w-full">
                {error}
              </p>
            )}

            {/* Formato de referencia */}
            <div className="w-full max-w-lg bg-gray-900 rounded-xl p-5 text-sm font-mono text-green-400 leading-relaxed">
              <p className="text-gray-500 mb-2">{"// casos.json — formato esperado"}</p>
              <p>{"{"}</p>
              <p className="pl-4">{"\"cases\": ["}</p>
              <p className="pl-8">{"{"}</p>
              <p className="pl-10">{"\"id_caso\": \"caso_001\","}</p>
              <p className="pl-10">{"\"descripcion\": \"Foto real tienda - azul\","}</p>
              <p className="pl-10">{"\"id_correcto\": \"AIM-P001-001\","}</p>
              <p className="pl-10">{"\"tipo\": \"foto_real\""}</p>
              <p className="pl-8">{"}"}</p>
              <p className="pl-4">{"]"}</p>
              <p>{"}"}</p>
            </div>

            <div className="w-full max-w-lg">
              <CriteriaLegend />
            </div>
          </div>
        )}

        {/* ══════════════════════════════════════════ EVALUATING */}
        {phase === "evaluating" && currentCase && session && (
          <>
            {/* Barra de progreso */}
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2 rounded-full transition-all duration-700"
                style={{
                  width: `${(session.current_idx / session.cases.length) * 100}%`,
                }}
              />
            </div>

            {/* Info del caso */}
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 flex justify-between items-center">
              <div>
                {currentCase.tipo && (
                  <span className="text-xs font-bold text-blue-600 uppercase tracking-wider">
                    {currentCase.tipo}
                  </span>
                )}
                <h2 className="text-lg font-bold text-gray-800 mt-0.5">
                  {currentCase.descripcion}
                </h2>
                <p className="text-xs text-gray-400 font-mono mt-1">
                  ID correcto esperado:{" "}
                  <strong className="text-gray-700">
                    {currentCase.id_correcto}
                  </strong>
                </p>
              </div>
              <div className="text-right flex-shrink-0 ml-4">
                <span className="text-4xl font-black text-gray-100">
                  {String(session.current_idx + 1).padStart(2, "0")}
                </span>
                <p className="text-xs text-gray-400">
                  de {session.cases.length}
                </p>
              </div>
            </div>

            {/* Criterios — siempre visibles en pantalla (requisito Fase 3) */}
            <CriteriaLegend />

            {/* ── Foto de consulta arriba (Fase 3) ── */}
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
              <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">
                📸 Imagen de consulta
              </h3>
              <div className="flex flex-col sm:flex-row gap-5 items-start">
                {!queryPreview ? (
                  <label className="flex-1 cursor-pointer border-2 border-dashed border-gray-200 rounded-xl p-8 flex flex-col items-center gap-2 hover:border-blue-300 hover:bg-blue-50 transition-all">
                    <span className="text-4xl">📷</span>
                    <span className="text-sm font-semibold text-gray-600">
                      Sube la foto de consulta de este caso
                    </span>
                    <span className="text-xs text-gray-400">
                      Nunca del catálogo — foto real externa
                    </span>
                    <input
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(e) =>
                        e.target.files?.[0] &&
                        handleImageSelect(e.target.files[0])
                      }
                    />
                  </label>
                ) : (
                  <div className="flex gap-5 items-start">
                    <div className="relative w-44 h-44 rounded-xl overflow-hidden border border-gray-200 flex-shrink-0">
                      <img
                        src={queryPreview}
                        alt="Consulta"
                        className="w-full h-full object-cover"
                      />
                      <label className="absolute bottom-2 right-2 bg-white/90 text-xs font-bold px-2 py-1 rounded-lg cursor-pointer shadow hover:bg-white transition-colors">
                        Cambiar
                        <input
                          type="file"
                          accept="image/*"
                          className="hidden"
                          onChange={(e) =>
                            e.target.files?.[0] &&
                            handleImageSelect(e.target.files[0])
                          }
                        />
                      </label>
                    </div>
                    {apiResults.length === 0 && (
                      <button
                        onClick={handleSearch}
                        disabled={loading}
                        className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold py-3 px-6 rounded-xl shadow-lg disabled:opacity-50 hover:scale-105 transition-all flex items-center gap-2 self-center"
                      >
                        {loading ? (
                          <>
                            <svg
                              className="animate-spin h-4 w-4"
                              viewBox="0 0 24 24"
                            >
                              <circle
                                className="opacity-25"
                                cx="12"
                                cy="12"
                                r="10"
                                stroke="currentColor"
                                strokeWidth="4"
                              />
                              <path
                                className="opacity-75"
                                fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                              />
                            </svg>
                            Buscando...
                          </>
                        ) : (
                          "Buscar similares →"
                        )}
                      </button>
                    )}
                  </div>
                )}
              </div>
              {error && (
                <p className="mt-3 text-red-600 text-sm bg-red-50 px-3 py-2 rounded-lg border border-red-100">
                  {error}
                </p>
              )}
            </div>

            {/* ── 5 resultados abajo, 3 botones por resultado (Fase 3) ── */}
            {apiResults.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest">
                  🔍 5 resultados del buscador — califica cada uno
                </h3>

                {apiResults.map((result, idx) => {
                  const score = result.score_reranking ?? result.score ?? 0;
                  const isCorrect = result.id === currentCase.id_correcto;
                  const rated = ratings[result.id];

                  return (
                    <div
                      key={result.id}
                      className={`bg-white rounded-2xl border shadow-sm p-5 flex gap-4 items-start transition-all ${
                        isCorrect
                          ? "border-emerald-200 bg-emerald-50/30"
                          : "border-gray-100"
                      } ${rated ? "opacity-80" : ""}`}
                    >
                      {/* Número de posición */}
                      <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center font-black text-gray-500 text-sm flex-shrink-0 mt-0.5">
                        {idx + 1}
                      </div>

                      {/* Imagen del resultado */}
                      <div className="w-28 h-28 flex-shrink-0 rounded-xl overflow-hidden bg-gray-100 border border-gray-100">
                        {result.imagen ? (
                          <img
                            src={`/api/images/${result.imagen}`}
                            alt={result.nombre}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              (e.target as HTMLImageElement).src = `https://placehold.co/112x112?text=${result.id.slice(-3)}`;
                            }}
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                            Sin imagen
                          </div>
                        )}
                      </div>

                      {/* Info + botones */}
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-start gap-2 mb-1">
                          <div className="min-w-0">
                            <p className="font-bold text-gray-900 truncate">
                              {result.nombre}
                            </p>
                            <p className="text-xs text-gray-400 font-mono">
                              {result.id}
                            </p>
                            {isCorrect && (
                              <span className="inline-block mt-1 text-xs bg-emerald-100 text-emerald-700 font-bold px-2 py-0.5 rounded-full">
                                ✓ ID correcto
                              </span>
                            )}
                          </div>
                          <span className="bg-indigo-50 text-indigo-700 font-black px-3 py-1.5 rounded-xl text-sm border border-indigo-100 flex-shrink-0">
                            {(score * 100).toFixed(1)}%
                          </span>
                        </div>

                        {/* 3 botones de juicio */}
                        <div className="flex gap-2 mt-3 flex-wrap">
                          {(["Acierto", "Sirve", "No sirve"] as Rating[]).map(
                            (r) => {
                              const active = rated === r;
                              const colorMap = {
                                Acierto: {
                                  active:
                                    "bg-emerald-500 text-white border-emerald-500 shadow-md shadow-emerald-100",
                                  idle: "bg-white text-emerald-700 border-emerald-200 hover:bg-emerald-50",
                                },
                                Sirve: {
                                  active:
                                    "bg-amber-500 text-white border-amber-500 shadow-md shadow-amber-100",
                                  idle: "bg-white text-amber-700 border-amber-200 hover:bg-amber-50",
                                },
                                "No sirve": {
                                  active:
                                    "bg-rose-500 text-white border-rose-500 shadow-md shadow-rose-100",
                                  idle: "bg-white text-rose-700 border-rose-200 hover:bg-rose-50",
                                },
                              };
                              return (
                                <button
                                  key={r}
                                  onClick={() => handleRate(result.id, r)}
                                  className={`px-4 py-2 rounded-xl text-sm font-bold border transition-all ${
                                    active
                                      ? colorMap[r].active
                                      : colorMap[r].idle
                                  }`}
                                >
                                  {r}
                                </button>
                              );
                            }
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}

                {/* Botón siguiente caso */}
                <button
                  onClick={handleNextCase}
                  disabled={!allRated}
                  className={`w-full py-4 rounded-2xl font-black text-lg transition-all ${
                    allRated
                      ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-xl hover:scale-[1.01] hover:shadow-2xl active:scale-[0.99]"
                      : "bg-gray-100 text-gray-400 cursor-not-allowed"
                  }`}
                >
                  {allRated
                    ? session.current_idx + 1 >= session.cases.length
                      ? "Finalizar y ver métricas →"
                      : `Siguiente caso (${session.current_idx + 2} / ${session.cases.length}) →`
                    : `Califica los ${apiResults.length - Object.keys(ratings).length} resultado(s) que faltan`}
                </button>
              </div>
            )}
          </>
        )}

        {/* ════════════════════════════════════════════════ DONE */}
        {phase === "done" && session && (
          <div className="flex flex-col items-center gap-8">
            <div className="text-center">
              <div className="text-6xl mb-4">🎉</div>
              <h2 className="text-3xl font-black text-gray-800 mb-1">
                Evaluación completada
              </h2>
              <p className="text-gray-400 text-sm">
                {session.evals.length} casos · {new Date().toLocaleDateString("es-PE")}
              </p>
            </div>

            {/* Los tres números (Fase 5) */}
            <div className="w-full grid grid-cols-1 sm:grid-cols-3 gap-4">
              <MetricCard
                label="Precision@1"
                value={metrics.p1}
                description="¿El primer resultado fue el diseño correcto?"
                gradient="bg-gradient-to-br from-blue-500 to-blue-700"
              />
              <MetricCard
                label="Recall@5"
                value={metrics.r5}
                description="¿El correcto apareció en alguno de los 5 resultados?"
                gradient="bg-gradient-to-br from-indigo-500 to-indigo-700"
              />
              <MetricCard
                label="Utilidad Top 5"
                value={metrics.util}
                description="¿Los resultados alternativos serían útiles para el cliente?"
                gradient="bg-gradient-to-br from-violet-500 to-violet-700"
              />
            </div>

            {/* Interpretación */}
            <div className="w-full bg-white rounded-2xl border border-gray-100 shadow-sm p-5 space-y-3">
              <h3 className="font-bold text-gray-700 text-sm uppercase tracking-wide mb-2">
                Interpretación
              </h3>
              <InterpretRow label="Precision@1" value={metrics.p1} />
              <InterpretRow label="Recall@5" value={metrics.r5} />
              <InterpretRow label="Utilidad" value={metrics.util} />
            </div>

            {/* Criterios */}
            <div className="w-full">
              <CriteriaLegend />
            </div>

            {/* Acciones */}
            <div className="flex gap-4 w-full flex-wrap">
              <button
                onClick={() => exportCSV(session.evals)}
                className="flex-1 bg-gray-900 text-white font-bold py-4 px-6 rounded-2xl hover:bg-gray-800 transition-colors flex items-center justify-center gap-2"
              >
                📥 Exportar evaluacion.csv
              </button>
              <button
                onClick={resetSession}
                className="px-6 py-4 rounded-2xl border border-gray-200 text-gray-600 font-bold hover:bg-gray-50 transition-colors"
              >
                Nueva sesión
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
