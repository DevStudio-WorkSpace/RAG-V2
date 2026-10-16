"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import { Icons } from "./Icons";
import { CATALOG_JERSEYS } from "@/lib/catalog";

interface SidebarProps {
  sidebarOpen: boolean;
  onClose: () => void;
  onSelectSample?: (sampleId: string) => void;
}

export default function Sidebar({
  sidebarOpen,
  onClose,
  onSelectSample,
}: SidebarProps) {
  const [quantity, setQuantity] = useState(14);
  const [selectedFabric, setSelectedFabric] = useState("Win Micro-Perforado Dry-Max");
  const [selectedCollar, setSelectedCollar] = useState("Cuello en V Anatómico");
  const [includeNames, setIncludeNames] = useState(true);
  const [includeShield, setIncludeShield] = useState(true);

  // Unit pricing calculation based on volume tiers
  const unitPrice = useMemo(() => {
    if (quantity >= 30) return 32;
    if (quantity >= 12) return 38;
    return 48;
  }, [quantity]);

  const estimatedTotal = useMemo(() => {
    return quantity * unitPrice;
  }, [quantity, unitPrice]);

  const whatsappMessage = encodeURIComponent(
    `Hola Atelier Sublitex, deseo cotizar una confección de camisetas personalizadas:
• Cantidad: ${quantity} unidades
• Precio estimado: S/ ${unitPrice} c/u (Total aprox: S/ ${estimatedTotal})
• Tejido: ${selectedFabric}
• Cuello: ${selectedCollar}
• Nombres y dorsales: ${includeNames ? "Sí" : "No"}
• Escudo de equipo: ${includeShield ? "Sí" : "No"}

¿Podrían indicarme los tiempos de entrega y métodos de pago?`
  );

  return (
    <>
      {/* Background Dim Backdrop */}
      <div
        className={`fixed inset-0 z-40 bg-black/70 backdrop-blur-sm transition-opacity duration-300 ${
          sidebarOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        }`}
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Slide-over Atelier Drawer */}
      <aside
        className={`fixed top-0 right-0 z-50 h-full w-full max-w-md bg-[var(--bg-subtle)] border-l border-[var(--border)] shadow-2xl transition-transform duration-300 ease-out flex flex-col ${
          sidebarOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {/* Drawer Header */}
        <div className="p-6 border-b border-[var(--border)] flex items-center justify-between">
          <div>
            <div className="text-[11px] font-semibold tracking-[0.2em] text-[#C5A880] uppercase">
              Sastrería & Confección Deportiva
            </div>
            <h2 className="text-base font-bold text-[var(--foreground-heading)] mt-0.5">
              Cotizador & Atelier a Medida
            </h2>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-lg text-[var(--foreground-muted)] hover:text-[var(--foreground)] hover:bg-white/5 transition-colors cursor-pointer"
            aria-label="Cerrar panel"
          >
            <Icons.X className="w-5 h-5" />
          </button>
        </div>

        {/* Drawer Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-7">
          {/* 1. Volume Calculator */}
          <section className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-[var(--foreground-heading)] uppercase tracking-wider">
                1. Cantidad de Camisetas
              </span>
              <span className="text-sm font-bold font-mono text-[#C5A880] tabular-nums">
                {quantity} prendas
              </span>
            </div>

            <input
              type="range"
              min="1"
              max="60"
              step="1"
              value={quantity}
              onChange={(e) => setQuantity(Number(e.target.value))}
              className="w-full accent-[#C5A880] cursor-pointer"
            />

            <div className="flex justify-between text-[11px] text-[var(--foreground-subtle)]">
              <span>1 unidad (Muestra)</span>
              <span>12 (Equipo)</span>
              <span>30+ (Liga / Mayor)</span>
            </div>

            {/* Price Preview Box */}
            <div className="p-4 rounded-xl border border-[var(--border)] bg-[var(--input-bg)] flex items-center justify-between">
              <div>
                <div className="text-xs text-[var(--foreground-muted)]">Precio unitario escala</div>
                <div className="text-lg font-bold font-mono text-[var(--foreground-heading)] tabular-nums">
                  S/ {unitPrice} <span className="text-xs font-normal text-[var(--foreground-subtle)]">/ camiseta</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs text-[var(--foreground-muted)]">Subtotal estimado</div>
                <div className="text-lg font-bold font-mono text-[#C5A880] tabular-nums">
                  S/ {estimatedTotal}
                </div>
              </div>
            </div>
          </section>

          {/* 2. Fabric Selection */}
          <section className="space-y-3">
            <span className="text-xs font-bold text-[var(--foreground-heading)] uppercase tracking-wider block">
              2. Tejido Deportivo Técnico
            </span>
            <div className="grid grid-cols-1 gap-2">
              {[
                {
                  name: "Win Micro-Perforado Dry-Max",
                  desc: "145g · Alta transpirabilidad con protección UV",
                },
                {
                  name: "Poliéster Piqué Interlock Heavy",
                  desc: "180g · Tacto formal, ideal para polos y retro",
                },
                {
                  name: "Micro-Mesh Jacquard Pro",
                  desc: "135g · Máxima ligereza para alta competencia",
                },
              ].map((fabric) => (
                <button
                  key={fabric.name}
                  onClick={() => setSelectedFabric(fabric.name)}
                  className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                    selectedFabric === fabric.name
                      ? "border-[#C5A880] bg-[rgba(197,168,128,0.06)]"
                      : "border-[var(--border)] bg-[var(--input-bg)] hover:border-[var(--border-strong)]"
                  }`}
                >
                  <div className="text-xs font-semibold text-[var(--foreground-heading)]">
                    {fabric.name}
                  </div>
                  <div className="text-[11px] text-[var(--foreground-muted)] mt-0.5">
                    {fabric.desc}
                  </div>
                </button>
              ))}
            </div>
          </section>

          {/* 3. Collar Style */}
          <section className="space-y-3">
            <span className="text-xs font-bold text-[var(--foreground-heading)] uppercase tracking-wider block">
              3. Tipo de Cuello & Acabado
            </span>
            <div className="grid grid-cols-3 gap-2">
              {["Cuello en V Anatómico", "Cuello Polo Camisero", "Cuello Redondo Match"].map(
                (collar) => (
                  <button
                    key={collar}
                    onClick={() => setSelectedCollar(collar)}
                    className={`p-2.5 rounded-xl border text-center transition-all text-xs cursor-pointer ${
                      selectedCollar === collar
                        ? "border-[#C5A880] bg-[rgba(197,168,128,0.08)] text-[var(--foreground-heading)] font-semibold"
                        : "border-[var(--border)] bg-[var(--input-bg)] text-[var(--foreground-muted)] hover:text-white"
                    }`}
                  >
                    {collar}
                  </button>
                )
              )}
            </div>
          </section>

          {/* 4. Customization Toggles */}
          <section className="space-y-2.5">
            <span className="text-xs font-bold text-[var(--foreground-heading)] uppercase tracking-wider block">
              4. Personalización Incluida
            </span>
            <div className="space-y-2 text-xs">
              <label className="flex items-center justify-between p-3 rounded-xl border border-[var(--border)] bg-[var(--input-bg)] cursor-pointer">
                <span className="text-[var(--foreground)]">Dorsales y nombres individuales</span>
                <input
                  type="checkbox"
                  checked={includeNames}
                  onChange={(e) => setIncludeNames(e.target.checked)}
                  className="w-4 h-4 accent-[#C5A880] rounded cursor-pointer"
                />
              </label>

              <label className="flex items-center justify-between p-3 rounded-xl border border-[var(--border)] bg-[var(--input-bg)] cursor-pointer">
                <span className="text-[var(--foreground)]">Escudo del club sublimado HD</span>
                <input
                  type="checkbox"
                  checked={includeShield}
                  onChange={(e) => setIncludeShield(e.target.checked)}
                  className="w-4 h-4 accent-[#C5A880] rounded cursor-pointer"
                />
              </label>
            </div>
          </section>

          {/* 5. Quick Sample Presets */}
          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-[var(--foreground-heading)] uppercase tracking-wider">
                Modelos de Referencia
              </span>
              <Link
                href="/catalog"
                onClick={onClose}
                className="text-xs text-[#C5A880] hover:underline"
              >
                Ver Catálogo Completo →
              </Link>
            </div>

            <div className="grid grid-cols-2 gap-2.5">
              {CATALOG_JERSEYS.slice(0, 4).map((j) => (
                <div
                  key={j.id}
                  onClick={() => {
                    if (onSelectSample && j.sampleQueryId) {
                      onSelectSample(j.sampleQueryId);
                    }
                    onClose();
                  }}
                  className="p-2.5 rounded-xl border border-[var(--border)] bg-[var(--input-bg)] hover:border-[#C5A880]/50 transition-all cursor-pointer group"
                >
                  <div className="aspect-[4/3] rounded-lg overflow-hidden bg-black/20 mb-2">
                    <img
                      src={j.image}
                      alt={j.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  </div>
                  <div className="text-xs font-semibold text-[var(--foreground-heading)] truncate">
                    {j.name}
                  </div>
                  <div className="text-[11px] text-[var(--foreground-muted)]">
                    S/ {j.priceTeam} en equipo
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* Drawer Action Footer */}
        <div className="p-6 border-t border-[var(--border)] space-y-3">
          <a
            href={`https://wa.me/?text=${whatsappMessage}`}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full py-3.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-lg transition-all active:scale-95"
          >
            <Icons.MessageCircle className="w-4 h-4" />
            <span>Solicitar Cotización por WhatsApp</span>
          </a>
          <p className="text-[11px] text-center text-[var(--foreground-subtle)]">
            Asesoría directa con nuestro maestro de confección y patronaje textil.
          </p>
        </div>
      </aside>
    </>
  );
}
