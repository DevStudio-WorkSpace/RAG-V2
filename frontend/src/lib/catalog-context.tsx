"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import {
  toCatalogJersey,
  type CatalogJersey,
  type ProductoCatalogo,
} from "./catalog";

interface CatalogState {
  catalog: CatalogJersey[];
  loading: boolean;
}

const CatalogContext = createContext<CatalogState>({
  catalog: [],
  loading: true,
});

export function CatalogProvider({ children }: { children: ReactNode }) {
  const [catalog, setCatalog] = useState<CatalogJersey[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    fetch("/api/catalog", { cache: "no-store" })
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json() as Promise<{ productos?: ProductoCatalogo[] }>;
      })
      .then((data) => {
        if (!active) return;
        const productos = Array.isArray(data.productos) ? data.productos : [];
        setCatalog(productos.map(toCatalogJersey));
      })
      .catch(() => {
        if (active) setCatalog([]);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  return (
    <CatalogContext.Provider value={{ catalog, loading }}>
      {children}
    </CatalogContext.Provider>
  );
}

export function useCatalog(): CatalogState {
  return useContext(CatalogContext);
}
