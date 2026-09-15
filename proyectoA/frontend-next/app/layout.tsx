import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Image from "next/image";
import "./globals.css";
import ThemeToggle from "./components/ThemeToggle";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Sublitex — Búsqueda visual",
  description: "Buscador visual de camisetas deportivas",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="es" data-theme="dark" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body>
        <nav className="site-nav">
          <div className="nav-brand">
            <Image
              src="/sublitex.png"
              alt="Sublitex"
              width={36}
              height={36}
              className="nav-logo"
            />
            <span className="nav-brand-text">Sublitex</span>
          </div>
          <div className="nav-links">
            <a href="/">Búsqueda</a>
            <a href="/evaluacion">Evaluador</a>
          </div>
          <ThemeToggle />
        </nav>
        {children}
      </body>
    </html>
  );
}
