import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/ThemeProvider";
import SidebarLayout from "./sidebar-layout";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Atelier Sublitex | Búsqueda Visual de Camisetas",
  description: "Atelier Sublitex - Búsqueda visual por imagen para encontrar camisetas deportivas y cotizar confección a medida con IA.",
  applicationName: "Atelier Sublitex",
  openGraph: {
    title: "Atelier Sublitex | Búsqueda Visual de Camisetas",
    description: "Encuentra camisetas deportivas por imagen y cotiza confección a medida.",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Atelier Sublitex | Búsqueda Visual de Camisetas",
    description: "Encuentra camisetas deportivas por imagen y cotiza confección a medida.",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="es"
      data-theme="dark"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-full flex">
        <ThemeProvider>
          <SidebarLayout>{children}</SidebarLayout>
        </ThemeProvider>
      </body>
    </html>
  );
}
