"use client";

import Link from "next/link";
import { Icons } from "@/components/Icons";

const DEMO_CASES = [
  {
    id: "caso_tienda",
    title: "Foto real tomada en tienda o perchero con celular",
    category: "Foto Móvil",
    description: "Una foto tomada rápidamente en una tienda departamental o estadio con iluminación artificial y percheros alrededor.",
    howItWorks: "El modelo aísla automáticamente el torso de la camiseta, eliminando el fondo comercial y percheros para concentrarse en las franjas y el escudo.",
    image: "/images/peru_home.jpg",
    matchedJersey: "Perú 2024 / 2025 — Franja Oficial Titular",
    accuracy: "98.5%",
  },
  {
    id: "caso_redes",
    title: "Captura de pantalla de redes sociales o TV en vivo",
    category: "Redes & Transmisión",
    description: "Una captura de pantalla de un reel de Instagram o partido transmitido en vivo donde los jugadores están en movimiento.",
    howItWorks: "Normaliza la saturación cromática y extrae patrones heráldicos y simetría geométrica para encontrar el club exacto.",
    image: "/images/argentina.jpg",
    matchedJersey: "Argentina 2024 — Tres Estrellas Conmemorativa",
    accuracy: "97.8%",
  },
  {
    id: "caso_clasico",
    title: "Diseño vintage o retro con detalles clásicos",
    category: "Archivo Histórico",
    description: "Una camiseta de una temporada pasada con cuello camisero formal, solapas y combinación cromática tradicional.",
    howItWorks: "Compara la estructura de diseño base e identifica alternativas de la misma era que el cliente puede confeccionar a medida.",
    image: "/images/catalog_heritage_retro.jpg",
    matchedJersey: "Heritage Tailored Striped Polo — Royal & Aurum",
    accuracy: "98.8%",
  },
  {
    id: "caso_sublimacion",
    title: "Diseño gráfico o mockup digital para confección de equipo",
    category: "Bespoke & Diseño",
    description: "Un archivo gráfico plano de un diseño personalizado preparado para la liga de fútbol o campeonato de fin de semana.",
    howItWorks: "Extrae paletas de color exactas y recomienda el gramaje y tejido sublimado compatible con esa densidad gráfica.",
    image: "/images/hero_atelier_jersey.jpg",
    matchedJersey: "Atelier Sublitex Gold Edition — Navy & Champagne",
    accuracy: "99.2%",
  },
];

export default function EvalPage() {
  return (
    <div className="space-y-12">
      {/* ── Header ── */}
      <section className="space-y-3.5">
        <div className="text-[11px] font-semibold tracking-[0.22em] text-[#C5A880] uppercase">
          Atelier Sublitex · Laboratorio de Reconocimiento Visual
        </div>
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-[var(--foreground-heading)] [text-wrap:balance]">
          Muestrario Real · Precisión y Casos de Confección
        </h1>
        <p className="text-base sm:text-lg text-[var(--foreground-muted)] max-w-2xl leading-relaxed">
          Diseñado para el mundo real: no necesitas fotos de estudio perfectas. Nuestro motor visual reconoce camisetas en situaciones cotidianas de compra, transmisiones o diseños mockups.
        </p>
      </section>

      {/* ── Demo Grid ── */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-7">
        {DEMO_CASES.map((demo) => (
          <div
            key={demo.id}
            className="p-6 rounded-2xl border border-[var(--border)] bg-[var(--bg-surface)] hover:border-[#C5A880]/50 transition-all flex flex-col justify-between shadow-lg space-y-5"
          >
            <div className="space-y-4">
              <div className="w-full aspect-[16/9] rounded-xl overflow-hidden bg-black/40 border border-[var(--border)] relative">
                <img
                  src={demo.image}
                  alt={demo.title}
                  className="w-full h-full object-cover"
                />
                <span className="absolute top-3 left-3 px-2.5 py-1 rounded-md bg-black/70 backdrop-blur-md text-white text-[11px] font-mono border border-white/10">
                  {demo.category}
                </span>
                <span className="absolute top-3 right-3 px-2.5 py-1 rounded-md bg-emerald-500/20 text-emerald-400 text-[11px] font-mono font-bold border border-emerald-500/30 backdrop-blur-md">
                  {demo.accuracy} similitud
                </span>
              </div>

              <div>
                <h3 className="text-lg font-bold text-[var(--foreground-heading)]">
                  {demo.title}
                </h3>
                <p className="text-xs text-[var(--foreground-muted)] mt-1.5 leading-relaxed">
                  {demo.description}
                </p>
              </div>

              <div className="p-3.5 rounded-xl bg-[var(--input-bg)] border border-[var(--border-subtle)] text-xs space-y-1">
                <span className="text-[#C5A880] font-semibold block text-[11px] uppercase tracking-wider">
                  Procesamiento en el Atelier
                </span>
                <p className="text-[var(--foreground-muted)] leading-relaxed">
                  {demo.howItWorks}
                </p>
              </div>
            </div>

            <div className="pt-3 flex items-center justify-between border-t border-[var(--border)]">
              <div className="text-xs">
                <span className="text-[var(--foreground-subtle)]">Resultado: </span>
                <span className="font-semibold text-[var(--foreground-heading)]">
                  {demo.matchedJersey}
                </span>
              </div>

              <Link
                href="/search"
                className="px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider bg-[#C5A880] hover:bg-[#D4AF37] text-[#0A0D14] flex items-center gap-1.5 transition-all active:scale-95"
              >
                <span>Probar</span>
                <Icons.ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        ))}
      </section>

      {/* ── Production Standards ── */}
      <section className="p-7 rounded-2xl border border-[var(--border)] bg-gradient-to-br from-white/[0.02] to-transparent space-y-5">
        <div>
          <div className="text-[11px] font-semibold tracking-[0.2em] text-[#C5A880] uppercase">
            Estándares de Sastrería Deportiva
          </div>
          <h2 className="text-xl font-bold text-[var(--foreground-heading)] mt-1">
            Garantía Textil & Confección para Equipos
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 text-xs text-[var(--foreground-muted)]">
          <div className="p-5 rounded-xl bg-[var(--input-bg)] border border-[var(--border-subtle)] space-y-2">
            <div className="font-bold text-[var(--foreground-heading)] text-sm">
              01. Fibras Técnicas Dry-Max
            </div>
            <p className="leading-relaxed text-[var(--foreground-muted)]">
              Tejidos microperforados de 145g con tratamiento hidrofílico que expulsa el sudor y filtro solar UPF 40+ para alto rendimiento.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-[var(--input-bg)] border border-[var(--border-subtle)] space-y-2">
            <div className="font-bold text-[var(--foreground-heading)] text-sm">
              02. Sublimación UltraHD a 205°C
            </div>
            <p className="leading-relaxed text-[var(--foreground-muted)]">
              Tintas reactivas de formulación italiana con fijación molecular que garantizan colores vibrantes sin decoloración tras más de 80 lavados.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-[var(--input-bg)] border border-[var(--border-subtle)] space-y-2">
            <div className="font-bold text-[var(--foreground-heading)] text-sm">
              03. Costuras Flatlock Reforzadas
            </div>
            <p className="leading-relaxed text-[var(--foreground-muted)]">
              Ensamblaje con hilo de poliéster de 5 cabos que evita rozaduras en el cuerpo del deportista y resiste tirones en competencia.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
