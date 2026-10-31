"use client";

import { useState, useMemo, useEffect } from "react";
import Link from "next/link";
import { CATALOG_JERSEYS, type CatalogJersey } from "@/lib/catalog";
import { Icons } from "@/components/Icons";

const ITEMS_PER_PAGE = 24;

export default function CatalogPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedJersey, setSelectedJersey] = useState<CatalogJersey | null>(null);
  const [page, setPage] = useState(1);

  const filtered = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (q === "") return CATALOG_JERSEYS;
    return CATALOG_JERSEYS.filter((jersey) => {
      return (
        jersey.id.toLowerCase().includes(q) ||
        jersey.name.toLowerCase().includes(q)
      );
    });
  }, [searchQuery]);

  useEffect(() => {
    setPage(1);
  }, [searchQuery]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / ITEMS_PER_PAGE));
  const safePage = Math.min(page, totalPages);
  const start = (safePage - 1) * ITEMS_PER_PAGE;
  const end = start + ITEMS_PER_PAGE;
  const paged = filtered.slice(start, end);

  const goToPage = (p: number) => {
    setPage(Math.min(Math.max(1, p), totalPages));
    if (typeof window !== "undefined") {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  return (
    <div className="space-y-12">
      {/* ── Header Section ── */}
      <section className="space-y-3.5">
        <div className="text-[11px] font-semibold tracking-[0.22em] text-[#C5A880] uppercase">
          Atelier Sublitex · Archivo & Confección Deportiva
        </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-[var(--foreground-heading)] [text-wrap:balance]">
          Catálogo Oficial
        </h1>
        <p className="text-base sm:text-lg text-[var(--foreground-muted)] max-w-2xl leading-relaxed">
          Catálogo completo con todos los modelos disponibles. Todos los precios son <span className="text-[#C5A880] font-semibold">a consultar</span>. Cotiza directo por WhatsApp con cantidad, tallas y personalización.
        </p>
      </section>

      {/* ── Filter & Search Toolbar ── */}
      <section className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 p-4 rounded-2xl border border-[var(--border)] bg-[var(--bg-surface)] backdrop-blur-md">
        {/* Search Input */}
        <div className="relative flex-1">
          <Icons.Search className="w-4 h-4 text-[var(--foreground-subtle)] absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="search"
            placeholder="Buscar por equipo, selección, código o país..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[var(--input-bg)] border border-[var(--border)] text-xs text-[var(--foreground)] placeholder-[var(--foreground-subtle)] focus:outline-none focus:border-[#C5A880]/60 transition-all"
            aria-label="Buscar en catálogo"
          />
        </div>

        <div className="flex items-center gap-2 text-xs text-[var(--foreground-muted)]">
          <span className="px-2.5 py-1 rounded-lg border border-[var(--border)] bg-[var(--input-bg)]">
            {filtered.length} modelos · Página {safePage} / {totalPages}
          </span>
        </div>
      </section>

      {/* ── Product Grid ── */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
        {paged.map((jersey) => {
          const whatsappQuote = encodeURIComponent(
            `Hola Atelier Sublitex, me interesa cotizar la camiseta ${jersey.name} (Código: ${jersey.id}) que vi en su catálogo para mi equipo.`
          );

          return (
            <div
              key={jersey.id}
              className="atelier-card flex flex-col justify-between overflow-hidden group"
            >
              <div>
                {/* Photo showcase with hover reveal */}
              <button
                type="button"
                onClick={() => setSelectedJersey(jersey)}
                className="w-full aspect-[4/3] bg-black/30 overflow-hidden relative cursor-pointer text-left"
                aria-label={`Ver ficha técnica de ${jersey.name}`}
              >
                <img
                  src={jersey.image}
                  alt={jersey.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  loading="lazy"
                />
                <div className="absolute top-3 left-3 px-2.5 py-1 rounded-md bg-black/60 backdrop-blur-md text-white text-[11px] font-mono border border-white/10">
                  {jersey.id}
                </div>
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-bold gap-1.5">
                  <Icons.Maximize2 className="w-4 h-4" />
                  <span>Ver Ficha de Patronaje</span>
                </div>
              </button>

                {/* Details */}
                <div className="p-6 space-y-3.5">
                  <div>
                    {/* Unboxed clean metadata */}
                    <div className="text-xs text-[var(--foreground-muted)] flex items-center gap-2 mb-1">
                      <span>{jersey.collection}</span>
                      <span aria-hidden="true">·</span>
                      <span>{jersey.season}</span>
                      <span aria-hidden="true">·</span>
                      <span>{jersey.fit}</span>
                    </div>
                    <h3 className="text-base font-bold text-[var(--foreground-heading)] leading-snug">
                      {jersey.name}
                    </h3>
                  </div>

                  <p className="text-xs text-[var(--foreground-muted)] line-clamp-2 leading-relaxed">
                    {jersey.description}
                  </p>

                  {/* Pricing info */}
                  <div className="pt-2 border-t border-[var(--border)] flex items-center justify-between text-xs">
                    <div>
                    <span className="text-[var(--foreground-subtle)] block text-[11px]">Precio:</span>
                    <span className="font-bold font-mono text-[#C5A880] text-sm tabular-nums">
                      A consultar
                    </span>
                    </div>

                    <div className="text-right">
                  <span className="text-[var(--foreground-subtle)] block text-[11px]">Entrega</span>
                  <span className="font-semibold text-[var(--foreground)] text-xs">
                    {jersey.turnaround}
                  </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5 pt-1">
                    <span className="text-[11px] text-[var(--foreground-subtle)]">Código:</span>
                    <span className="text-[11px] font-mono text-[var(--foreground-heading)]">{jersey.id}</span>
                  </div>
                </div>
              </div>

              {/* Card Footer Actions */}
              <div className="p-5 sm:p-6 pt-0 flex items-center gap-2.5">
                <Link
                  href="/search"
                  className="flex-1 py-2.5 px-3 rounded-xl text-xs font-semibold border border-[var(--border)] bg-[var(--input-bg)] text-[var(--foreground)] hover:border-[#C5A880]/50 flex items-center justify-center gap-1.5 transition-all text-center"
                >
                  <Icons.Search className="w-3.5 h-3.5 text-[#C5A880]" />
                  <span>Buscar Similares</span>
                </Link>

                <a
                  href={`https://wa.me/?text=${encodeURIComponent(`Hola Atelier Sublitex, me interesa cotizar el modelo ${jersey.id} (${jersey.name}) del catálogo oficial. Cantidad: ____ Tallas: ____ Nombres/dorsales: ____ Logos: ____`)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="py-2.5 px-4 rounded-xl text-xs font-bold uppercase tracking-wider bg-emerald-600 hover:bg-emerald-500 text-white flex items-center justify-center gap-1.5 shadow-md transition-all active:scale-95"
                  title="Cotizar por WhatsApp"
                >
                  <Icons.MessageCircle className="w-4 h-4" />
                  <span>Cotizar</span>
                </a>
              </div>
            </div>
          );
        })}
      </section>

      {totalPages > 1 && (
        <section className="flex flex-col sm:flex-row items-center justify-between gap-3 p-4 rounded-2xl border border-[var(--border)] bg-[var(--bg-surface)]">
          <div className="text-xs text-[var(--foreground-muted)]">
            Mostrando {start + 1}-{Math.min(end, filtered.length)} de {filtered.length}
          </div>
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => goToPage(safePage - 1)}
              disabled={safePage === 1}
              className="px-3 py-1.5 rounded-lg text-xs border border-[var(--border)] bg-[var(--input-bg)] disabled:opacity-40 disabled:cursor-not-allowed hover:border-[#C5A880]/50"
            >
              Anterior
            </button>
            <button
              onClick={() => goToPage(safePage + 1)}
              disabled={safePage === totalPages}
              className="px-3 py-1.5 rounded-lg text-xs border border-[var(--border)] bg-[var(--input-bg)] disabled:opacity-40 disabled:cursor-not-allowed hover:border-[#C5A880]/50"
            >
              Siguiente
            </button>
          </div>
        </section>
      )}

      {/* ── Modal for Technical Specifications ── */}
      {selectedJersey && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 animate-fade-in">
          <div className="bg-[var(--bg-subtle)] border border-[var(--border)] rounded-2xl max-w-2xl w-full p-6 space-y-5 shadow-2xl overflow-y-auto max-h-[90vh]">
            <div className="flex items-center justify-between pb-3.5 border-b border-[var(--border)]">
              <div>
                <span className="text-[11px] text-[#C5A880] font-bold uppercase tracking-wider">
                  Especificaciones Técnicas & Patronaje
                </span>
                <h3 className="text-lg font-bold text-[var(--foreground-heading)] mt-0.5">
                  {selectedJersey.name}
                </h3>
              </div>
              <button
                onClick={() => setSelectedJersey(null)}
                className="p-1.5 rounded-lg text-[var(--foreground-muted)] hover:text-white transition-colors cursor-pointer"
              >
                <Icons.X className="w-5 h-5" />
              </button>
            </div>

            <div className="w-full aspect-[16/9] rounded-xl overflow-hidden bg-black/40 border border-[var(--border)]">
              <img
                src={selectedJersey.image}
                alt={selectedJersey.name}
                className="w-full h-full object-cover"
              />
            </div>

            <p className="text-xs text-[var(--foreground-muted)] leading-relaxed">
              {selectedJersey.description}
            </p>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3.5 rounded-xl bg-[var(--input-bg)] border border-[var(--border-subtle)]">
                <span className="text-[var(--foreground-subtle)] block text-[11px]">Tejido Recomendado</span>
                <span className="font-bold text-[var(--foreground-heading)] mt-0.5 block">
                  {selectedJersey.sublimationSpecs.fabric}
                </span>
              </div>
              <div className="p-3.5 rounded-xl bg-[var(--input-bg)] border border-[var(--border-subtle)]">
                <span className="text-[var(--foreground-subtle)] block text-[11px]">Tipo de Cuello</span>
                <span className="font-bold text-[var(--foreground-heading)] mt-0.5 block">
                  {selectedJersey.sublimationSpecs.collar}
                </span>
              </div>
              <div className="p-3.5 rounded-xl bg-[var(--input-bg)] border border-[var(--border-subtle)]">
                <span className="text-[var(--foreground-subtle)] block text-[11px]">Corte de Manga</span>
                <span className="font-bold text-[var(--foreground-heading)] mt-0.5 block">
                  {selectedJersey.sublimationSpecs.sleeve}
                </span>
              </div>
              <div className="p-3.5 rounded-xl bg-[var(--input-bg)] border border-[var(--border-subtle)]">
                <span className="text-[var(--foreground-subtle)] block text-[11px]">Técnica de Sublimado</span>
                <span className="font-bold text-[var(--foreground-heading)] mt-0.5 block">
                  {selectedJersey.sublimationSpecs.printType}
                </span>
              </div>
            </div>

            {/* Price Tiers */}
            <div className="p-4 rounded-xl border border-[var(--border)] bg-[var(--input-bg)] flex items-center justify-between text-xs">
              <div>
                <span className="text-[var(--foreground-subtle)] block text-[11px]">Muestra Individual</span>
                <span className="font-bold font-mono text-[var(--foreground-heading)] text-sm">
                  S/ {selectedJersey.priceRetail}
                </span>
              </div>
              <div>
                <span className="text-[var(--foreground-subtle)] block text-[11px]">Equipo (12+)</span>
                <span className="font-bold font-mono text-[#C5A880] text-sm">
                  S/ {selectedJersey.priceTeam} c/u
                </span>
              </div>
              <div>
                <span className="text-[var(--foreground-subtle)] block text-[11px]">Liga / Torneo (30+)</span>
                <span className="font-bold font-mono text-emerald-400 text-sm">
                  S/ {selectedJersey.priceLeague} c/u
                </span>
              </div>
            </div>

            <div className="pt-3.5 border-t border-[var(--border)] flex justify-end gap-3">
              <button
                onClick={() => setSelectedJersey(null)}
                className="px-4 py-2.5 rounded-xl text-xs font-semibold border border-[var(--border)] text-[var(--foreground-muted)] hover:text-white cursor-pointer"
              >
                Cerrar
              </button>
              <a
                href={`https://wa.me/?text=${encodeURIComponent(
                  `Hola Atelier Sublitex, vi la ficha técnica de la camiseta ${selectedJersey.name} (Código: ${selectedJersey.id}) y deseo cotizarla.`
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
