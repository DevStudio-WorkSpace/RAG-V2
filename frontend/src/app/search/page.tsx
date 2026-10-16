"use client";

import { useState, useRef, useCallback, useMemo, useEffect } from "react";
import { CATALOG_JERSEYS, type CatalogJersey } from "@/lib/catalog";
import { identifyCountry } from "@/lib/countries";
import type { SearchResult, ApiResult } from "@/lib/types";
import { searchImage } from "@/lib/api";
import { Icons } from "@/components/Icons";
import { ResultCardSkeleton } from "@/components/Skeleton";

export default function SearchPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<SearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [dragging, setDragging] = useState(false);

  // Modals for details & comparison
  const [selectedJerseyModal, setSelectedJerseyModal] = useState<CatalogJersey | null>(null);
  const [compareModal, setCompareModal] = useState<{ query: string; match: ApiResult } | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load image from File
  const handleFile = useCallback((f: File) => {
    if (!f.type.startsWith("image/")) {
      setError("Por favor sube un archivo de imagen válido (JPG, PNG o WEBP).");
      return;
    }
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError(null);
  }, []);

  // One-click sample selector
  const handleSelectSample = useCallback(async (sample: CatalogJersey) => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch(sample.image);
      const blob = await res.blob();
      const sampleFile = new File([blob], `${sample.id.toLowerCase()}.jpg`, { type: "image/jpeg" });

      setFile(sampleFile);
      setPreview(sample.image);

      const apiEndpoint = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const { data, error: err } = await searchImage(apiEndpoint, sampleFile, "fusion");
      setLoading(false);
      if (err) {
        setError(err);
      } else {
        setResult(data);
      }
    } catch {
      setLoading(false);
      setError("No se pudo cargar la imagen de prueba seleccionada.");
    }
  }, []);

  // Trigger search on uploaded file
  const handleSearch = useCallback(async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    const apiEndpoint = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const { data, error: err } = await searchImage(apiEndpoint, file, "fusion");
    setLoading(false);
    if (err) {
      setError(err);
    } else {
      setResult(data);
    }
  }, [file]);

  // Handle Drag & Drop
  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const f = e.dataTransfer.files[0];
      if (f) handleFile(f);
    },
    [handleFile]
  );

  // Paste image from clipboard (Ctrl+V)
  useEffect(() => {
    const handlePaste = (e: ClipboardEvent) => {
      const items = e.clipboardData?.items;
      if (!items) return;
      for (let i = 0; i < items.length; i++) {
        if (items[i].type.startsWith("image/")) {
          const blob = items[i].getAsFile();
          if (blob) handleFile(blob);
          break;
        }
      }
    };
    window.addEventListener("paste", handlePaste);
    return () => window.removeEventListener("paste", handlePaste);
  }, [handleFile]);

  const resultados = useMemo(() => result?.resultados ?? [], [result]);

  return (
    <div className="space-y-12">
      {/* ── 1. Hero Section ── */}
      <section className="space-y-4 text-left">
        <div className="text-[11px] font-semibold tracking-[0.22em] text-[#C5A880] uppercase">
          Atelier Sublitex · Reconocimiento Visual de Camisetas
        </div>

        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-[var(--foreground-heading)] max-w-3xl [text-wrap:balance]">
          Encuentra o confecciona cualquier camiseta deportiva a partir de una foto
        </h1>

        <p className="text-base sm:text-lg text-[var(--foreground-muted)] max-w-2xl leading-relaxed">
          Sube una foto tomada en una tienda, captura de partido en TV o diseño digital. Nuestro motor visual reconoce el diseño y te conecta con el catálogo de confección a medida de alta gama.
        </p>
      </section>

      {/* ── 2. One-Click Sample Presets ── */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-[var(--foreground-subtle)]">
            ¿Deseas probar ahora? Selecciona un modelo de muestra:
          </span>
          <span className="text-xs text-[#C5A880] font-medium hidden sm:inline">
            1 clic para analizar
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {CATALOG_JERSEYS.slice(0, 6).map((sample) => (
            <button
              key={sample.id}
              onClick={() => handleSelectSample(sample)}
              className="p-3 rounded-xl border border-[var(--border)] bg-[var(--input-bg)] hover:border-[#C5A880]/50 transition-all text-left group cursor-pointer active:scale-95 flex flex-col justify-between"
            >
              <div className="w-full aspect-[4/3] rounded-lg overflow-hidden bg-black/20 mb-2.5 relative">
                <img
                  src={sample.image}
                  alt={sample.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <div>
                <div className="text-xs font-bold text-[var(--foreground-heading)] truncate">
                  {sample.name}
                </div>
                <div className="text-[11px] text-[var(--foreground-muted)] truncate mt-0.5">
                  {sample.team}
                </div>
              </div>
            </button>
          ))}
        </div>
      </section>

      {/* ── 3. Image Upload Zone ── */}
      <section className="space-y-4">
        <input
          ref={fileInputRef}
          type="file"
          accept=".jpg,.jpeg,.png,.webp"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />

        {!file ? (
          /* Empty Dropzone */
          <div
            className={`dropzone-atelier p-10 sm:p-14 text-center flex flex-col items-center justify-center min-h-[280px] ${
              dragging ? "is-active" : ""
            }`}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => {
              e.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
          >
            <div className="w-14 h-14 rounded-xl bg-[rgba(197,168,128,0.08)] border border-[rgba(197,168,128,0.25)] flex items-center justify-center text-[#C5A880] mb-4">
              <Icons.Upload className="w-6 h-6" />
            </div>

            <h2 className="text-lg font-bold text-[var(--foreground-heading)] mb-1.5">
              Arrastra tu imagen aquí o haz clic para explorar tus archivos
            </h2>

            <p className="text-xs sm:text-sm text-[var(--foreground-muted)] max-w-md leading-relaxed">
              Compatible con fotos tomadas con celular, capturas de pantalla o mockups gráficos. También puedes presionar <kbd className="px-1.5 py-0.5 rounded bg-white/10 font-mono text-[11px]">Ctrl+V</kbd> para pegar directamente.
            </p>
          </div>
        ) : (
          /* Active Query Review Box */
          <div className="p-6 rounded-2xl border border-[var(--border)] bg-[var(--bg-surface)] backdrop-blur-md space-y-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-5 border-b border-[var(--border)]">
              <div className="flex items-center gap-3.5">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/25 flex items-center justify-center text-emerald-400">
                  <Icons.Check className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-[11px] uppercase tracking-wider font-bold text-[#C5A880]">
                    Imagen Cargada y Lista para Analizar
                  </div>
                  <div className="text-sm font-bold text-[var(--foreground-heading)] truncate max-w-sm sm:max-w-md">
                    {file.name}
                  </div>
                  <div className="text-xs text-[var(--foreground-muted)] font-mono">
                    {(file.size / 1024).toFixed(1)} KB
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-3 w-full sm:w-auto">
                <button
                  onClick={handleSearch}
                  disabled={loading}
                  className="w-full sm:w-auto px-6 py-3 rounded-xl font-bold text-xs uppercase tracking-wider bg-[#C5A880] hover:bg-[#D4AF37] text-[#0A0D14] active:scale-95 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <Icons.RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Analizando diseño...</span>
                    </>
                  ) : (
                    <>
                      <Icons.Search className="w-4 h-4" />
                      <span>Buscar en Catálogo</span>
                    </>
                  )}
                </button>

                <button
                  onClick={() => {
                    setFile(null);
                    setPreview(null);
                    setResult(null);
                  }}
                  className="px-4 py-3 rounded-xl text-xs font-semibold uppercase tracking-wider border border-[var(--border)] bg-[var(--input-bg)] text-[var(--foreground-muted)] hover:text-[var(--foreground)] transition-all cursor-pointer"
                >
                  Cambiar
                </button>
              </div>
            </div>

            {/* Preview Box */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div className="p-4 rounded-xl border border-[var(--border)] bg-[var(--input-bg)] flex flex-col items-center">
                <span className="text-xs text-[var(--foreground-muted)] mb-3 font-semibold self-start uppercase tracking-wider">
                  Foto de Consulta
                </span>
                {preview && (
                  <div className="w-full h-64 rounded-lg overflow-hidden bg-black/30 flex items-center justify-center border border-[var(--border-subtle)]">
                    <img
                      src={preview}
                      alt="Foto de consulta"
                      className="max-h-full max-w-full object-contain"
                    />
                  </div>
                )}
              </div>

              <div className="p-4 rounded-xl border border-[var(--border)] bg-[var(--input-bg)] flex flex-col justify-between">
                <div>
                  <span className="text-xs text-[var(--foreground-muted)] mb-3 font-semibold block uppercase tracking-wider">
                    Reconocimiento & Comparación Textil
                  </span>
                  <div className="space-y-3.5 text-xs text-[var(--foreground-muted)] mt-2">
                    <div className="flex items-start gap-2.5">
                      <Icons.CheckCircle2 className="w-4 h-4 text-[#C5A880] flex-shrink-0 mt-0.5" />
                      <span>Aísla el torso de la prenda, neutralizando fondos y percheros.</span>
                    </div>
                    <div className="flex items-start gap-2.5">
                      <Icons.CheckCircle2 className="w-4 h-4 text-[#C5A880] flex-shrink-0 mt-0.5" />
                      <span>Extrae la paleta cromática, geometría de bastones y escudos.</span>
                    </div>
                    <div className="flex items-start gap-2.5">
                      <Icons.CheckCircle2 className="w-4 h-4 text-[#C5A880] flex-shrink-0 mt-0.5" />
                      <span>Entrega ficha técnica con opciones de tela sublimada para tu equipo.</span>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-[var(--border)] flex items-center justify-between text-xs text-[var(--foreground-muted)]">
                  <span>Modo: Multimodal Fashion-CLIP</span>
                  <span className="text-[#C5A880] font-semibold">Listo para buscar</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* ── Error Notification ── */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-400 text-sm flex items-center gap-3">
          <Icons.AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* ── Loading Skeleton ── */}
      {loading && (
        <section className="space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[var(--border)]">
            <span className="text-sm font-bold text-[#C5A880] flex items-center gap-2">
              <Icons.RefreshCw className="w-4 h-4 animate-spin" />
              Comparando con toda la colección del catálogo...
            </span>
          </div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <ResultCardSkeleton key={i} />
            ))}
          </div>
        </section>
      )}

      {/* ── 4. Search Results ── */}
      {!loading && resultados.length > 0 && (
        <section className="space-y-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-[var(--border)]">
            <div>
              <h2 className="text-xl font-bold text-[var(--foreground-heading)]">
                Modelos Coincidentes Encontrados ({resultados.length})
              </h2>
              <p className="text-xs text-[var(--foreground-muted)] mt-0.5">
                Clasificados por similitud de patronaje, estructura gráfica y paleta de color.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-5">
            {resultados.map((r, idx) => {
              const rank = idx + 1;
              const pct = Math.max(0, Math.min(100, (r.score_reranking ?? r.score) * 100));
              const country = identifyCountry(r.nombre, r.id);
              const matchedJersey = CATALOG_JERSEYS.find(
                (j) => j.id === r.id || r.nombre.includes(j.team) || j.name.includes(r.nombre)
              );

              const whatsappText = encodeURIComponent(
                `Hola Atelier Sublitex, vi la camiseta ${r.nombre} (ID: ${r.id}) en su buscador con ${pct.toFixed(1)}% de coincidencia y deseo cotizar la confección para mi equipo.`
              );

              return (
                <div
                  key={r.id}
                  className="p-6 rounded-2xl border border-[var(--border)] bg-[var(--bg-surface)] hover:border-[#C5A880]/50 transition-all flex flex-col md:flex-row items-start gap-6 shadow-lg group"
                >
                  {/* Photo with zoom trigger */}
                  <div
                    onClick={() => matchedJersey && setSelectedJerseyModal(matchedJersey)}
                    className="relative w-full md:w-56 aspect-[4/3] md:aspect-square rounded-xl overflow-hidden bg-black/30 border border-[var(--border)] flex-shrink-0 cursor-pointer group/img"
                  >
                    <img
                      src={r.imagen}
                      alt={r.nombre}
                      className="w-full h-full object-cover group-hover/img:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover/img:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-semibold gap-1.5">
                      <Icons.Maximize2 className="w-4 h-4" />
                      <span>Ver Ficha Técnica</span>
                    </div>
                  </div>

                  {/* Details */}
                  <div className="flex-1 min-w-0 w-full space-y-3.5">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        {/* Clean unboxed metadata with dot separators */}
                        <div className="text-xs text-[var(--foreground-muted)] flex items-center gap-2">
                          <span className="font-bold text-[var(--foreground-heading)]">#{rank}</span>
                          <span aria-hidden="true">·</span>
                          <span>Código {r.id}</span>
                          {matchedJersey && (
                            <>
                              <span aria-hidden="true">·</span>
                              <span>{matchedJersey.collection}</span>
                            </>
                          )}
                        </div>
                        <h3 className="text-lg font-bold text-[var(--foreground-heading)] mt-0.5">
                          {r.nombre}
                        </h3>
                      </div>

                      {/* Match Accuracy Indicator */}
                      <div className="text-right flex-shrink-0">
                        <div className="text-xl font-extrabold font-mono text-[#C5A880] tabular-nums">
                          {pct.toFixed(1)}%
                        </div>
                        <div className="text-[11px] text-[var(--foreground-subtle)]">
                          {pct >= 95 ? "Coincidencia exacta" : pct >= 85 ? "Alta similitud" : "Alternativa de diseño"}
                        </div>
                      </div>
                    </div>

                    {/* Metadata line */}
                    <div className="flex flex-wrap items-center gap-3 text-xs text-[var(--foreground-muted)]">
                      {country && (
                        <span>{country.info.nombre_completo} ({country.info.seleccion})</span>
                      )}
                      {matchedJersey && (
                        <>
                          <span aria-hidden="true">·</span>
                          <span>{matchedJersey.league}</span>
                          <span aria-hidden="true">·</span>
                          <span>{matchedJersey.season}</span>
                          <span aria-hidden="true">·</span>
                          <span>Corte: {matchedJersey.fit}</span>
                        </>
                      )}
                    </div>

                    {/* Technical & Commercial specs */}
                    {matchedJersey && (
                      <div className="p-3.5 rounded-xl border border-[var(--border-subtle)] bg-[var(--input-bg)] text-xs text-[var(--foreground-muted)] flex flex-wrap gap-x-6 gap-y-2">
                        <div>
                          <span className="text-[var(--foreground-subtle)]">Tejido:</span>{" "}
                          <span className="font-semibold text-[var(--foreground-heading)]">
                            {matchedJersey.sublimationSpecs.fabric}
                          </span>
                        </div>
                        <div>
                          <span className="text-[var(--foreground-subtle)]">Precio equipo (12+):</span>{" "}
                          <span className="font-bold font-mono text-[#C5A880] tabular-nums">
                            S/ {matchedJersey.priceTeam} c/u
                          </span>
                        </div>
                        <div>
                          <span className="text-[var(--foreground-subtle)]">Tiempo de entrega:</span>{" "}
                          <span className="font-semibold text-[var(--foreground-heading)]">
                            {matchedJersey.turnaround}
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
                      <div className="flex items-center gap-2.5 flex-wrap">
                        {preview && (
                          <button
                            onClick={() => setCompareModal({ query: preview, match: r })}
                            className="px-3.5 py-2 rounded-lg text-xs font-semibold border border-[var(--border)] bg-[var(--input-bg)] hover:border-[#C5A880]/50 text-[var(--foreground)] flex items-center gap-1.5 transition-all cursor-pointer"
                          >
                            <Icons.Sliders className="w-3.5 h-3.5 text-[#C5A880]" />
                            <span>Comparar con mi foto</span>
                          </button>
                        )}

                        {matchedJersey && (
                          <button
                            onClick={() => setSelectedJerseyModal(matchedJersey)}
                            className="px-3.5 py-2 rounded-lg text-xs font-semibold border border-[var(--border)] bg-[var(--input-bg)] hover:border-[#C5A880]/50 text-[var(--foreground)] flex items-center gap-1.5 transition-all cursor-pointer"
                          >
                            <Icons.Info className="w-3.5 h-3.5" />
                            <span>Ficha de Patronaje</span>
                          </button>
                        )}
                      </div>

                      {/* Instant WhatsApp Quote */}
                      <a
                        href={`https://wa.me/?text=${whatsappText}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider bg-emerald-600 hover:bg-emerald-500 text-white flex items-center gap-2 shadow-md transition-all active:scale-95"
                      >
                        <Icons.MessageCircle className="w-4 h-4" />
                        <span>Cotizar Confección</span>
                      </a>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* ── 5. Comparison Modal ── */}
      {compareModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 animate-fade-in">
          <div className="bg-[var(--bg-subtle)] border border-[var(--border)] rounded-2xl max-w-3xl w-full p-6 space-y-6 shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-[var(--border)]">
              <div>
                <span className="text-[11px] font-semibold tracking-[0.2em] text-[#C5A880] uppercase">
                  Comparador Visual de Similitud
                </span>
                <h3 className="text-base font-bold text-[var(--foreground-heading)] mt-0.5">
                  {compareModal.match.nombre}
                </h3>
              </div>
              <button
                onClick={() => setCompareModal(null)}
                className="p-1.5 rounded-lg text-[var(--foreground-muted)] hover:text-white transition-colors cursor-pointer"
              >
                <Icons.X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <div className="space-y-2 text-center">
                <span className="text-xs font-semibold text-[var(--foreground-muted)] uppercase tracking-wider">
                  Foto de Consulta
                </span>
                <div className="aspect-[4/3] rounded-xl overflow-hidden bg-black/40 border border-[var(--border)] flex items-center justify-center">
                  <img
                    src={compareModal.query}
                    alt="Tu foto"
                    className="max-h-full max-w-full object-contain"
                  />
                </div>
              </div>

              <div className="space-y-2 text-center">
                <span className="text-xs font-semibold text-[#C5A880] uppercase tracking-wider">
                  Resultado en Catálogo ({((compareModal.match.score_reranking ?? compareModal.match.score) * 100).toFixed(1)}%)
                </span>
                <div className="aspect-[4/3] rounded-xl overflow-hidden bg-black/40 border border-[#C5A880]/40 flex items-center justify-center">
                  <img
                    src={compareModal.match.imagen}
                    alt="Resultado"
                    className="max-h-full max-w-full object-contain"
                  />
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-[var(--border)] flex justify-end gap-3">
              <button
                onClick={() => setCompareModal(null)}
                className="px-4 py-2.5 rounded-xl text-xs font-semibold border border-[var(--border)] text-[var(--foreground-muted)] hover:text-white cursor-pointer"
              >
                Cerrar
              </button>
              <a
                href={`https://wa.me/?text=${encodeURIComponent(
                  `Hola Atelier Sublitex, comparé mi foto con el modelo ${compareModal.match.nombre} (ID: ${compareModal.match.id}) y deseo cotizar la confección.`
                )}`}
                target="_blank"
                rel="noopener noreferrer"
                className="px-5 py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider bg-emerald-600 hover:bg-emerald-500 text-white flex items-center gap-2 shadow-md"
              >
                <Icons.MessageCircle className="w-4 h-4" />
                <span>Cotizar Este Modelo</span>
              </a>
            </div>
          </div>
        </div>
      )}

      {/* ── 6. Technical Sheet Modal ── */}
      {selectedJerseyModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 animate-fade-in">
          <div className="bg-[var(--bg-subtle)] border border-[var(--border)] rounded-2xl max-w-2xl w-full p-6 space-y-5 shadow-2xl overflow-y-auto max-h-[90vh]">
            <div className="flex items-center justify-between pb-3.5 border-b border-[var(--border)]">
              <div>
                <span className="text-[11px] text-[#C5A880] font-bold uppercase tracking-wider">
                  Ficha Técnica & Patronaje Atelier
                </span>
                <h3 className="text-lg font-bold text-[var(--foreground-heading)]">
                  {selectedJerseyModal.name}
                </h3>
              </div>
              <button
                onClick={() => setSelectedJerseyModal(null)}
                className="p-1.5 rounded-lg text-[var(--foreground-muted)] hover:text-white transition-colors cursor-pointer"
              >
                <Icons.X className="w-5 h-5" />
              </button>
            </div>

            <div className="w-full aspect-[16/9] rounded-xl overflow-hidden bg-black/40 border border-[var(--border)]">
              <img
                src={selectedJerseyModal.image}
                alt={selectedJerseyModal.name}
                className="w-full h-full object-cover"
              />
            </div>

            <p className="text-xs text-[var(--foreground-muted)] leading-relaxed">
              {selectedJerseyModal.description}
            </p>

            {/* Sublimation & Quality Specs */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3.5 rounded-xl bg-[var(--input-bg)] border border-[var(--border-subtle)]">
                <span className="text-[var(--foreground-subtle)] block text-[11px]">Tejido Técnico</span>
                <span className="font-bold text-[var(--foreground-heading)] mt-0.5 block">
                  {selectedJerseyModal.sublimationSpecs.fabric}
                </span>
              </div>
              <div className="p-3.5 rounded-xl bg-[var(--input-bg)] border border-[var(--border-subtle)]">
                <span className="text-[var(--foreground-subtle)] block text-[11px]">Cuello & Acabado</span>
                <span className="font-bold text-[var(--foreground-heading)] mt-0.5 block">
                  {selectedJerseyModal.sublimationSpecs.collar}
                </span>
              </div>
              <div className="p-3.5 rounded-xl bg-[var(--input-bg)] border border-[var(--border-subtle)]">
                <span className="text-[var(--foreground-subtle)] block text-[11px]">Corte & Mangas</span>
                <span className="font-bold text-[var(--foreground-heading)] mt-0.5 block">
                  {selectedJerseyModal.sublimationSpecs.sleeve}
                </span>
              </div>
              <div className="p-3.5 rounded-xl bg-[var(--input-bg)] border border-[var(--border-subtle)]">
                <span className="text-[var(--foreground-subtle)] block text-[11px]">Técnica de Impresión</span>
                <span className="font-bold text-[var(--foreground-heading)] mt-0.5 block">
                  {selectedJerseyModal.sublimationSpecs.printType}
                </span>
              </div>
            </div>

            {/* Pricing Tiers */}
            <div className="p-4 rounded-xl border border-[var(--border)] bg-[var(--input-bg)] flex items-center justify-between text-xs">
              <div>
                <span className="text-[var(--foreground-subtle)] block text-[11px]">Muestra Individual</span>
                <span className="font-bold font-mono text-[var(--foreground-heading)] text-sm">
                  S/ {selectedJerseyModal.priceRetail}
                </span>
              </div>
              <div>
                <span className="text-[var(--foreground-subtle)] block text-[11px]">Equipo Completo (12+)</span>
                <span className="font-bold font-mono text-[#C5A880] text-sm">
                  S/ {selectedJerseyModal.priceTeam} c/u
                </span>
              </div>
              <div>
                <span className="text-[var(--foreground-subtle)] block text-[11px]">Liga / Torneo (30+)</span>
                <span className="font-bold font-mono text-emerald-400 text-sm">
                  S/ {selectedJerseyModal.priceLeague} c/u
                </span>
              </div>
            </div>

            <div className="pt-3.5 border-t border-[var(--border)] flex justify-end gap-3">
              <button
                onClick={() => setSelectedJerseyModal(null)}
                className="px-4 py-2.5 rounded-xl text-xs font-semibold border border-[var(--border)] text-[var(--foreground-muted)] hover:text-white cursor-pointer"
              >
                Cerrar
              </button>
              <a
                href={`https://wa.me/?text=${encodeURIComponent(
                  `Hola Atelier Sublitex, vi la ficha técnica de la camiseta ${selectedJerseyModal.name} (Código: ${selectedJerseyModal.id}) y deseo cotizarla para mi equipo.`
                )}`}
                target="_blank"
                rel="noopener noreferrer"
                className="px-5 py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider bg-emerald-600 hover:bg-emerald-500 text-white flex items-center gap-2 shadow-md"
              >
                <Icons.MessageCircle className="w-4 h-4" />
                <span>Cotizar por WhatsApp</span>
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
