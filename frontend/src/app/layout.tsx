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
  title: "Aimari RAG Visual - Búsqueda de Camisetas",
  description: "Búsqueda visual RAG y evaluación de camisetas deportivas con Fashion-CLIP, YOLO y reranking.",
  openGraph: {
    title: "Aimari RAG Visual - Búsqueda de Camisetas",
    description: "Búsqueda visual RAG y evaluación de camisetas deportivas con Fashion-CLIP, YOLO y reranking.",
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
