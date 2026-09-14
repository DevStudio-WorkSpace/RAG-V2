import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Búsqueda visual de camisetas",
  description: "Interfaz visual para buscar camisetas deportivas similares usando embeddings y búsqueda por imagen.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body>
        <nav className="site-nav">
          <a href="/">🔍 Búsqueda</a>
          <a href="/evaluacion">📋 Evaluador</a>
        </nav>
        {children}
      </body>
    </html>
  );
}
