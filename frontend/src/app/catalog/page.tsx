"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import { CATALOG_JERSEYS, type CatalogJersey } from "@/lib/catalog";
import { Icons } from "@/components/Icons";

export default function CatalogPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCollection, setSelectedCollection] = useState<string>("all");
  const [selectedJersey, setSelectedJersey] = useState<CatalogJersey | null>(null);

  const collections = useMemo(() => {
    const list = Array.from(new Set(CATALOG_JERSEYS.map((j) => j.collection)));
    return ["all", ...list];
  }, []);

  const filtered = useMemo(() => {
    return CATALOG_JERSEYS.filter((jersey) => {
      const matchesSearch =
        searchQuery === "" ||
        jersey.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        jersey.team.toLowerCase().includes(searchQuery.toLowerCase()) ||
        jersey.country.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesCollection =
        selectedCollection === "all" || jersey.collection === selectedCollection;

      return matchesSearch && matchesCollection;
    });
  }, [searchQuery, selectedCollection]);

  return (
    <div className="space-y-12">
      {/* ── Header Section ── */}
      <section className="space-y-3.5">
        <div className="text-[11px] font-semibold tracking-[0.22em] text-[#C5A880] uppercase">
          Atelier Sublitex · Archivo & Confección Deportiva
        </div>
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-[var(--foreground-heading)] [text-wrap:balance]">
          Catálogo Oficial de Camisetas Deportivas
        </h1>
        <p className="text-base sm:text-lg text-[var(--foreground-muted)] max-w-2xl leading-relaxed">
          Explora nuestra colección de alta gama: ediciones bespoke, selecciones internacionales, clubes de élite y líneas retro preparadas para confección y sublimación de precisión.
        </p>
      </section>

      {/* ── Filter & Search Toolbar ── */}
      <section className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 p-4 rounded-2xl border border-[var(--border)] bg-[var(--bg-surface)] backdrop-blur-md">
        {/* Search Input */}
        <div className="relative flex-1">
          <Icons.Search className="w-4 h-4 text-[var(--foreground-subtle)] absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Buscar por equipo, selección, código o país..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[var(--input-bg)] border border-[var(--border)] text-xs text-[var(--foreground)] placeholder-[var(--foreground-subtle)] focus:outline-none focus:border-[#C5A880]/60 transition-all"
          />
        </div>

        {/* Collection Selector */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
          <button
            onClick={() => setSelectedCollection("all")}
            className={`px-3.5 py-2 rounded-xl text-xs font-semibold uppercase tracking-wider transition-all whitespace-nowrap cursor-pointer ${
              selectedCollection === "all"
                ? "bg-[#C5A880] text-[#0A0D14] font-bold"
                : "bg-[var(--input-bg)] text-[var(--foreground-muted)] hover:text-white border border-[var(--border)]"
            }`}
          >
            Todas las Colecciones
          </button>
          {collections
            .filter((c) => c !== "all")
            .map((col) => (
              <button
                key={col}
                onClick={() => setSelectedCollection(col)}
                className={`px-3.5 py-2 rounded-xl text-xs font-semibold uppercase tracking-wider transition-all whitespace-nowrap cursor-pointer ${
                  selectedCollection === col
                    ? "bg-[#C5A880] text-[#0A0D14] font-bold"
                    : "bg-[var(--input-bg)] text-[var(--foreground-muted)] hover:text-white border border-[var(--border)]"
                }`}
              >
                {col}
              </button>
            ))}
        </div>
      </section>

      {/* ── Product Grid ── */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-7">
        {filtered.map((jersey) => {
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
                <div
                  onClick={() => setSelectedJersey(jersey)}
                  className="w-full aspect-[4/3] bg-black/30 overflow-hidden relative cursor-pointer"
                >
                  <img
                    src={jersey.image}
                    alt={jersey.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute top-3 left-3 px-2.5 py-1 rounded-md bg-black/60 backdrop-blur-md text-white text-[11px] font-mono border border-white/10">
                    {jersey.id}
                  </div>
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-bold gap-1.5">
                    <Icons.Maximize2 className="w-4 h-4" />
                    <span>Ver Ficha de Patronaje</span>
                  </div>
                </div>

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
                      <span className="text-[var(--foreground-subtle)] block text-[11px]">En equipo (12+):</span>
                      <span className="font-bold font-mono text-[#C5A880] text-sm tabular-nums">
                        S/ {jersey.priceTeam} <span className="text-[11px] font-normal text-[var(--foreground-subtle)]">c/u</span>
                      </span>
                    </div>

                    <div className="text-right">
                      <span className="text-[var(--foreground-subtle)] block text-[11px]">Entrega estimada:</span>
                      <span className="font-semibold text-[var(--foreground)] text-xs">
                        {jersey.turnaround}
                      </span>
                    </div>
                  </div>

                  {/* Color Swatches */}
                  <div className="flex items-center gap-1.5 pt-1">
                    <span className="text-[11px] text-[var(--foreground-subtle)] mr-1">Tonos:</span>
                    {jersey.colorHexes.map((hex, i) => (
                      <span
                        key={i}
                        className="w-3.5 h-3.5 rounded-full border border-white/20 shadow-sm"
                        style={{ backgroundColor: hex }}
                        title={jersey.colors[i] || hex}
                      />
                    ))}
                  </div>
                </div>
              </div>

              {/* Card Footer Actions */}
              <div className="p-6 pt-0 flex items-center gap-2.5">
                <Link
                  href="/search"
                  className="flex-1 py-2.5 px-3 rounded-xl text-xs font-semibold border border-[var(--border)] bg-[var(--input-bg)] text-[var(--foreground)] hover:border-[#C5A880]/50 flex items-center justify-center gap-1.5 transition-all text-center"
                >
                  <Icons.Search className="w-3.5 h-3.5 text-[#C5A880]" />
                  <span>Buscar Similares</span>
                </Link>

                <a
                  href={`https://wa.me/?text=${whatsappQuote}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="py-2.5 px-4 rounded-xl text-xs font-bold uppercase tracking-wider bg-emerald-600 hover:bg-emerald-500 text-white flex items-center justify-center gap-1.5 shadow-md transition-all active:scale-95"
                  title="Cotizar en WhatsApp"
                >
                  <Icons.MessageCircle className="w-4 h-4" />
                  <span>Cotizar</span>
                </a>
              </div>
            </div>
          );
        })}
      </section>

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
