"use client";

import { useState } from "react";
import { Icons } from "./Icons";
import { CATALOG_JERSEYS } from "@/lib/catalog";

interface SidebarProps {
  sidebarOpen: boolean;
  onClose: () => void;
}

const SIZES = ["XS", "S", "M", "L", "XL", "XXL", "3XL"];

export default function Sidebar({ sidebarOpen, onClose }: SidebarProps) {
  const [productId, setProductId] = useState<string>("");
  const [quantity, setQuantity] = useState(12);
  const [sizes, setSizes] = useState<Record<string, number>>({
    XS: 0, S: 2, M: 4, L: 4, XL: 2, XXL: 0, "3XL": 0,
  });
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [team, setTeam] = useState("");
  const [colors, setColors] = useState("");
  const [notes, setNotes] = useState("");
  const [namesNumbers, setNamesNumbers] = useState(true);
  const [logos, setLogos] = useState(true);

  const totalQty = Object.values(sizes).reduce((a, b) => a + b, 0);
  const qty = totalQty > 0 ? totalQty : quantity;

  const selectedProduct = CATALOG_JERSEYS.find((j) => j.id === productId);

  const toggleSize = (s: string, delta: number) => {
    setSizes((prev) => {
      const next = { ...prev, [s]: Math.max(0, (prev[s] || 0) + delta) };
      return next;
    });
  };

  const sizesText = SIZES.filter((s) => (sizes[s] || 0) > 0)
    .map((s) => `${s}: ${sizes[s]}`)
    .join(" | ");

  const whatsappMessage = encodeURIComponent(
    `*COTIZACIÓN ATELIER SUBLITEX*\n\n` +
    `*Producto:* ${selectedProduct ? `${selectedProduct.id} - ${selectedProduct.name}` : "Por definir / A partir de imagen"}\n` +
    `*Cantidad total:* ${qty} unidades\n` +
    `*Tallas:* ${sizesText || `General ${qty} unidades`}\n\n` +
    `*Datos:* \n` +
    `- Nombre/Contacto: ${name || "No indicado"}\n` +
    `- Teléfono/WhatsApp: ${phone || "No indicado"}\n` +
    `- Equipo/Club: ${team || "No indicado"}\n\n` +
    `*Personalización:* \n` +
    `- Colores/Diseño: ${colors || "Según modelo / Enviar imagen/referencia"}\n` +
    `- Nombres y dorsales: ${namesNumbers ? "Sí" : "No"}\n` +
    `- Logos/Escudos: ${logos ? "Sí" : "No"}\n\n` +
    `*Notas:* ${notes || "Sin notas"}\n\n` +
    `Quisiera recibir cotización con precio por unidad, total, tiempo de entrega y forma de pago.`
  );

  return (
    <>
      <div
        className={`fixed inset-0 z-40 bg-black/75 backdrop-blur-sm transition-opacity duration-300 ${
          sidebarOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        }`}
        onClick={onClose}
        aria-hidden="true"
      />

      <aside
        className={`fixed top-0 right-0 z-50 h-full w-full max-w-md bg-[var(--bg-subtle)] border-l border-[var(--border)] shadow-2xl transition-transform duration-300 ease-out flex flex-col ${
          sidebarOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="p-5 sm:p-6 border-b border-[var(--border)] flex items-center justify-between">
          <div>
            <div className="text-[11px] font-semibold tracking-[0.2em] text-[#C5A880] uppercase">
              Cotizador Rápido
            </div>
            <h2 className="text-base font-bold text-[var(--foreground-heading)] mt-0.5">
              Cotización por WhatsApp
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

        <div className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-6">
          <section className="space-y-2">
            <label className="text-xs font-bold text-[var(--foreground-heading)] uppercase tracking-wider">
              1) Modelo del catálogo
            </label>
            <select
              value={productId}
              onChange={(e) => setProductId(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl bg-[var(--input-bg)] border border-[var(--border)] text-xs text-[var(--foreground)] focus:outline-none focus:border-[#C5A880]/60"
            >
              <option value="">Por definir (enviar imagen/referencia)</option>
              {CATALOG_JERSEYS.slice(0, 80).map((j) => (
                <option key={j.id} value={j.id}>
                  {j.id} - {j.name}
                </option>
              ))}
            </select>
            {selectedProduct && (
              <div className="flex items-center gap-3 p-2.5 rounded-xl border border-[var(--border)] bg-[var(--input-bg)]">
                <div className="w-14 h-14 rounded-lg overflow-hidden bg-black/30 flex-shrink-0">
                  <img src={selectedProduct.image} alt={selectedProduct.id} className="w-full h-full object-cover" />
                </div>
                <div className="text-xs">
                  <div className="font-semibold text-[var(--foreground-heading)]">{selectedProduct.id}</div>
                  <div className="text-[var(--foreground-muted)]">Precio: A consultar</div>
                </div>
              </div>
            )}
          </section>

          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-[var(--foreground-heading)] uppercase tracking-wider">
                2) Tallas y cantidades
              </label>
              <span className="text-xs font-mono text-[#C5A880]">Total: {qty}</span>
            </div>
            <div className="grid grid-cols-7 gap-1.5">
              {SIZES.map((s) => (
                <div key={s} className="flex flex-col items-center gap-1">
                  <div className="text-[10px] text-[var(--foreground-muted)]">{s}</div>
                  <div className="flex flex-col items-center rounded-lg border border-[var(--border)] overflow-hidden">
                    <button onClick={() => toggleSize(s, 1)} className="px-1.5 py-0.5 text-xs hover:bg-white/5">+</button>
                    <div className="px-1.5 py-0.5 text-xs font-mono w-full text-center bg-[var(--input-bg)]">{sizes[s]}</div>
                    <button onClick={() => toggleSize(s, -1)} className="px-1.5 py-0.5 text-xs hover:bg-white/5">-</button>
                  </div>
                </div>
              ))}
            </div>
            <input
              type="number"
              min={1}
              value={quantity}
              onChange={(e) => setQuantity(Number(e.target.value) || 1)}
              className="w-full px-3 py-2 rounded-xl bg-[var(--input-bg)] border border-[var(--border)] text-xs"
              placeholder="O cantidad total si no desglosas tallas"
            />
          </section>

          <section className="space-y-2">
            <label className="text-xs font-bold text-[var(--foreground-heading)] uppercase tracking-wider">
              3) Datos de contacto
            </label>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Nombre y apellido" className="w-full px-3 py-2.5 rounded-xl bg-[var(--input-bg)] border border-[var(--border)] text-xs" />
            <input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="Teléfono / WhatsApp" className="w-full px-3 py-2.5 rounded-xl bg-[var(--input-bg)] border border-[var(--border)] text-xs" />
            <input value={team} onChange={(e) => setTeam(e.target.value)} placeholder="Equipo / Club / Empresa" className="w-full px-3 py-2.5 rounded-xl bg-[var(--input-bg)] border border-[var(--border)] text-xs" />
          </section>

          <section className="space-y-2">
            <label className="text-xs font-bold text-[var(--foreground-heading)] uppercase tracking-wider">
              4) Personalización
            </label>
            <input value={colors} onChange={(e) => setColors(e.target.value)} placeholder="Colores o referencia (nombre/código)" className="w-full px-3 py-2.5 rounded-xl bg-[var(--input-bg)] border border-[var(--border)] text-xs" />
            <label className="flex items-center justify-between p-2.5 rounded-xl border border-[var(--border)] bg-[var(--input-bg)] text-xs">
              <span>Nombres y dorsales</span>
              <input type="checkbox" checked={namesNumbers} onChange={(e) => setNamesNumbers(e.target.checked)} className="accent-[#C5A880]" />
            </label>
            <label className="flex items-center justify-between p-2.5 rounded-xl border border-[var(--border)] bg-[var(--input-bg)] text-xs">
              <span>Logos / Escudos</span>
              <input type="checkbox" checked={logos} onChange={(e) => setLogos(e.target.checked)} className="accent-[#C5A880]" />
            </label>
            <textarea value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Notas adicionales (telas, acabados, plazo, etc.)" className="w-full px-3 py-2.5 rounded-xl bg-[var(--input-bg)] border border-[var(--border)] text-xs min-h-[70px]" />
          </section>
        </div>

        <div className="p-5 sm:p-6 border-t border-[var(--border)] space-y-2">
          <a
            href={`https://wa.me/?text=${whatsappMessage}`}
            target="_blank"
            rel="noopener noreferrer"
            onClick={onClose}
            className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-lg transition-all active:scale-95"
          >
            <Icons.MessageCircle className="w-4 h-4" />
            <span>Enviar cotización por WhatsApp</span>
          </a>
          <p className="text-[10px] text-center text-[var(--foreground-subtle)]">
            Te responderemos con precio, tiempo de entrega y forma de pago.
          </p>
        </div>
      </aside>
    </>
  );
}
