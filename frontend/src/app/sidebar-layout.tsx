"use client";

import { useState, type ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import { Icons } from "@/components/Icons";
import { useTheme } from "@/components/ThemeProvider";

export default function SidebarLayout({ children }: { children: ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const pathname = usePathname();
  const { theme, toggle } = useTheme();

  return (
    <div className="min-h-screen flex flex-col w-full bg-[var(--bg-main)] text-[var(--foreground)] antialiased">
      {/* Slide-over Bespoke Kit & Quote Assistant */}
      <Sidebar
        sidebarOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* ── Top Bar Contract (3 Zones, gap-8) ── */}
      <header className="sticky top-0 z-30 h-16 border-b border-[var(--border)] bg-[var(--bg-surface-glass)] backdrop-blur-xl px-4 sm:px-8 flex items-center justify-between gap-8 transition-colors">
        {/* Zone 1: Single text wordmark */}
        <Link
          href="/search"
          className="text-base font-extrabold tracking-tight text-[var(--foreground-heading)] whitespace-nowrap shrink-0 flex items-center gap-2"
        >
          <span className="tracking-[0.18em] uppercase text-xs font-bold text-[#C5A880]">
            Atelier
          </span>
          <span className="font-bold tracking-tight text-white">Sublitex</span>
          <span className="w-1.5 h-1.5 rounded-full bg-[#C5A880]/70" />
        </Link>

        {/* Zone 2: 4 clean single-line nav links */}
        <nav className="hidden md:flex items-center gap-8 text-xs font-semibold uppercase tracking-wider text-[var(--foreground-muted)]">
          <Link
            href="/search"
            className={`hover:text-[var(--foreground-heading)] transition-colors whitespace-nowrap shrink-0 ${
              pathname === "/search" ? "text-[#C5A880] font-bold" : ""
            }`}
          >
            Buscador Visual
          </Link>
          <Link
            href="/catalog"
            className={`hover:text-[var(--foreground-heading)] transition-colors whitespace-nowrap shrink-0 ${
              pathname === "/catalog" ? "text-[#C5A880] font-bold" : ""
            }`}
          >
            Catálogo Oficial
          </Link>
          <Link
            href="/eval"
            className={`hover:text-[var(--foreground-heading)] transition-colors whitespace-nowrap shrink-0 ${
              pathname === "/eval" ? "text-[#C5A880] font-bold" : ""
            }`}
          >
            Muestrario Real
          </Link>
          <button
            onClick={() => setSidebarOpen(true)}
            className="hover:text-[var(--foreground-heading)] transition-colors whitespace-nowrap shrink-0 cursor-pointer"
          >
            Cotizador a Medida
          </button>
        </nav>

        {/* Zone 3: 1 Primary Action + Theme Toggle + Mobile Menu */}
        <div className="flex items-center gap-3 shrink-0">
          <Link
            href="/search"
            className="hidden sm:inline-flex px-4 py-2 text-xs font-bold uppercase tracking-wider text-[#0A0D14] bg-[#C5A880] hover:bg-[#D4AF37] rounded-lg transition-all whitespace-nowrap shrink-0 active:scale-95"
          >
            Subir Foto
          </Link>

          <button
            onClick={toggle}
            className="w-9 h-9 rounded-lg border border-[var(--border)] bg-[var(--input-bg)] flex items-center justify-center text-[var(--foreground-muted)] hover:text-[var(--foreground)] active:scale-95 transition-all cursor-pointer"
            aria-label="Alternar tema visual"
          >
            {theme === "dark" ? (
              <Icons.Sun className="w-4 h-4 text-[#C5A880]" />
            ) : (
              <Icons.Moon className="w-4 h-4 text-slate-700" />
            )}
          </button>

          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 rounded-lg border border-[var(--border)] bg-[var(--input-bg)] text-[var(--foreground-muted)] hover:text-[var(--foreground)] active:scale-95 transition-all flex items-center gap-1.5 cursor-pointer"
            title="Abrir cotizador de prendas"
          >
            <Icons.SlidersHorizontal className="w-4 h-4 text-[#C5A880]" />
            <span className="text-xs font-medium hidden lg:inline">Cotizar</span>
          </button>
        </div>
      </header>

      {/* ── Main Viewport Container ── */}
      <main className="flex-1 w-full max-w-[1360px] mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        {children}
      </main>

      {/* ── Refined Tailored Footer ── */}
      <footer className="border-t border-[var(--border)] bg-[var(--bg-subtle)] py-8 px-4 sm:px-8 text-xs text-[var(--foreground-muted)]">
        <div className="max-w-[1360px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="font-bold text-[var(--foreground-heading)]">Atelier Sublitex</span>
            <span aria-hidden="true">·</span>
            <span>Alta Sastrería Deportiva & Búsqueda Visual de Camisetas</span>
          </div>

          <div className="flex items-center gap-6">
            <Link href="/search" className="hover:text-[var(--foreground-heading)] transition-colors">
              Buscador por Imagen
            </Link>
            <Link href="/catalog" className="hover:text-[var(--foreground-heading)] transition-colors">
              Catálogo de Prendas
            </Link>
            <Link href="/eval" className="hover:text-[var(--foreground-heading)] transition-colors">
              Muestrario de Casos
            </Link>
            <button
              onClick={() => setSidebarOpen(true)}
              className="hover:text-[var(--foreground-heading)] transition-colors cursor-pointer"
            >
              Cotización Directa
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}
