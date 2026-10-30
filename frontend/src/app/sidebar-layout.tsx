"use client";

import { useState, type ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import { Icons } from "@/components/Icons";
import { useTheme } from "@/components/ThemeProvider";

const NAV_LINKS = [
  { href: "/search", label: "Buscador Visual" },
  { href: "/catalog", label: "Catálogo Oficial" },
  { href: "/eval", label: "Muestrario" },
];

export default function SidebarLayout({ children }: { children: ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const pathname = usePathname();
  const { theme, toggle } = useTheme();

  const closeMobileNav = () => setMobileNavOpen(false);

  return (
    <div className="min-h-screen flex flex-col w-full bg-[var(--bg-main)] text-[var(--foreground)] antialiased">
      {/* Cotizador */}
      <Sidebar
        sidebarOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* ── Top Bar Contract (3 Zones, gap-8) ── */}
      <header className="sticky top-0 z-30 h-16 border-b border-[var(--border)] bg-[var(--bg-surface-glass)] backdrop-blur-xl px-4 sm:px-6 lg:px-8 flex items-center justify-between gap-4 lg:gap-8 transition-colors">
        {/* Zone 1: Single text wordmark */}
        <Link
          href="/search"
          onClick={closeMobileNav}
          className="text-base font-extrabold tracking-tight text-[var(--foreground-heading)] whitespace-nowrap shrink-0 flex items-center gap-2"
        >
          <span className="tracking-[0.18em] uppercase text-[10px] sm:text-xs font-bold text-[#C5A880]">
            Atelier
          </span>
          <span className="font-bold tracking-tight text-[var(--foreground-heading)]">Sublitex</span>
          <span className="w-1.5 h-1.5 rounded-full bg-[#C5A880]/70 hidden sm:inline-block" />
        </Link>

        {/* Zone 2: Desktop nav links */}
        <nav className="hidden md:flex items-center gap-6 lg:gap-8 text-xs font-semibold uppercase tracking-wider text-[var(--foreground-muted)]">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`hover:text-[var(--foreground-heading)] transition-colors whitespace-nowrap shrink-0 ${
                pathname === link.href ? "text-[#C5A880] font-bold" : ""
              }`}
            >
              {link.label}
            </Link>
          ))}
          <button
            onClick={() => setSidebarOpen(true)}
            className="hover:text-[var(--foreground-heading)] transition-colors whitespace-nowrap shrink-0 cursor-pointer"
          >
            Cotizador
          </button>
        </nav>

        {/* Zone 3: Actions */}
        <div className="flex items-center gap-2 sm:gap-3 shrink-0">
          <Link
            href="/search"
            className="hidden sm:inline-flex px-3.5 lg:px-4 py-2 text-[11px] lg:text-xs font-bold uppercase tracking-wider text-[#0A0D14] bg-[#C5A880] hover:bg-[#D4AF37] rounded-lg transition-all whitespace-nowrap shrink-0 active:scale-95"
          >
            Subir Foto
          </Link>

          <button
            onClick={toggle}
            className="w-9 h-9 rounded-lg border border-[var(--border)] bg-[var(--input-bg)] flex items-center justify-center text-[var(--foreground-muted)] hover:text-[var(--foreground)] active:scale-95 transition-all cursor-pointer"
            aria-label="Alternar tema visual"
            title={theme === "dark" ? "Cambiar a tema claro" : "Cambiar a tema oscuro"}
          >
            {theme === "dark" ? (
              <Icons.Sun className="w-4 h-4 text-[#C5A880]" />
            ) : (
              <Icons.Moon className="w-4 h-4" />
            )}
          </button>

          <button
            onClick={() => setSidebarOpen(true)}
            className="hidden md:flex p-2 rounded-lg border border-[var(--border)] bg-[var(--input-bg)] text-[var(--foreground-muted)] hover:text-[var(--foreground)] active:scale-95 transition-all items-center gap-1.5 cursor-pointer"
            title="Abrir cotizador de prendas"
          >
            <Icons.SlidersHorizontal className="w-4 h-4 text-[#C5A880]" />
            <span className="text-xs font-medium hidden lg:inline">Cotizador</span>
          </button>

          <button
            onClick={() => setMobileNavOpen((v) => !v)}
            className="md:hidden w-9 h-9 rounded-lg border border-[var(--border)] bg-[var(--input-bg)] flex items-center justify-center text-[var(--foreground-muted)] hover:text-[var(--foreground)] active:scale-95 transition-all cursor-pointer"
            aria-label={mobileNavOpen ? "Cerrar menú" : "Abrir menú"}
            aria-expanded={mobileNavOpen}
          >
            {mobileNavOpen ? <Icons.X className="w-4 h-4" /> : <Icons.Menu className="w-4 h-4" />}
          </button>
        </div>
      </header>

      {/* Mobile Nav Menu */}
      {mobileNavOpen && (
        <div className="md:hidden fixed inset-x-0 top-16 z-40 border-b border-[var(--border)] bg-[var(--bg-surface-glass)] backdrop-blur-xl shadow-lg">
          <nav className="flex flex-col px-4 py-3 space-y-1">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={closeMobileNav}
                className={`px-3 py-2.5 rounded-lg text-sm font-semibold transition-colors ${
                  pathname === link.href
                    ? "text-[#C5A880] bg-[rgba(197,168,128,0.08)]"
                    : "text-[var(--foreground-muted)] hover:text-[var(--foreground-heading)] hover:bg-white/[0.02]"
                }`}
              >
                {link.label}
              </Link>
            ))}
            <button
              onClick={() => {
                closeMobileNav();
                setSidebarOpen(true);
              }}
              className="px-3 py-2.5 rounded-lg text-sm font-semibold text-left text-[var(--foreground-muted)] hover:text-[var(--foreground-heading)] hover:bg-white/[0.02] transition-colors"
            >
              Cotizador
            </button>
            <Link
              href="/search"
              onClick={closeMobileNav}
              className="mt-2 px-3 py-2.5 rounded-lg text-sm font-bold text-center text-[#0A0D14] bg-[#C5A880] hover:bg-[#D4AF37] transition-colors"
            >
              Subir Foto para Buscar
            </Link>
          </nav>
        </div>
      )}

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
