"use client";

import Link from "next/link";
import { Icons } from "@/components/Icons";
import { CATALOG_JERSEYS } from "@/lib/catalog";

export default function EvalPage() {
  const samples = CATALOG_JERSEYS.slice(0, 12);

  return (
    <div className="space-y-10 sm:space-y-12">
      <section className="space-y-3.5">
        <div className="text-[11px] font-semibold tracking-[0.22em] text-[#C5A880] uppercase">
          Atelier Sublitex · Catálogo Visual
        </div>
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-[var(--foreground-heading)] [text-wrap:balance]">
          Muestrario Real
        </h1>
        <p className="text-base sm:text-lg text-[var(--foreground-muted)] max-w-2xl leading-relaxed">
          Muestra directa del catálogo oficial. Usa el buscador visual para encontrar el modelo que busques o cotízalo directamente.
        </p>
      </section>

      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
        {samples.map((j) => (
          <div
            key={j.id}
            className="rounded-2xl border border-[var(--border)] bg-[var(--bg-surface)] overflow-hidden shadow-lg hover:border-[#C5A880]/50 transition-all group"
          >
            <div className="aspect-[4/3] bg-black/30 overflow-hidden relative">
              <img
                src={j.image}
                alt={j.id}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                loading="lazy"
              />
              <div className="absolute top-2 left-2 px-2 py-0.5 rounded-md bg-black/60 text-white text-[10px] font-mono">
                {j.id}
              </div>
            </div>
            <div className="p-4 space-y-3">
              <div>
                <div className="text-xs font-bold text-[var(--foreground-heading)] truncate">{j.name}</div>
                <div className="text-[11px] text-[var(--foreground-muted)]">Precio: A consultar</div>
              </div>
              <div className="flex items-center gap-2">
                <Link
                  href="/search"
                  className="flex-1 py-2 rounded-lg text-xs font-semibold border border-[var(--border)] bg-[var(--input-bg)] text-center hover:border-[#C5A880]/50 transition-all"
                >
                  Buscar
                </Link>
                <a
                  href={`https://wa.me/?text=${encodeURIComponent(`Hola Atelier Sublitex, me interesa cotizar el modelo ${j.id} del muestrario. Cantidad: ____ Tallas: ____`)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-2 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white flex items-center gap-1.5"
                >
                  <Icons.MessageCircle className="w-3.5 h-3.5" />
                  Cotizar
                </a>
              </div>
            </div>
          </div>
        ))}
      </section>

      <div className="flex justify-center">
        <Link
          href="/catalog"
          className="px-5 py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider bg-[#C5A880] hover:bg-[#D4AF37] text-[#0A0D14] flex items-center gap-2"
        >
          <span>Ver catálogo completo ({CATALOG_JERSEYS.length} modelos)</span>
          <Icons.ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
