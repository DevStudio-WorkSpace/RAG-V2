# Mapa de secciones visuales del frontend (Next.js)

> **Fecha:** 2026-10-23
> **Ubicación:** `frontend/`
> **Tipo:** Documentación visual / arquitectura de UI
> **Fuente de verdad de los cambios visuales:** `mejora del UI.md` (raíz del repo)

---

## 1. ¿Qué responde este documento?

Este archivo responde a la pregunta:

> **¿Qué carpeta o archivo del frontend altera cada sección visual de la interfaz?**

Y lo hace con un mapa explícito: cada sección visual de la app Next.js → el/los archivo(s) que la implementa o la modifican.

---

## 2. Mapa general: sección visual → archivo(s) que la alteran

| # | Sección visual | Carpeta / Archivo que la altera | Notas |
|---|---|---|---|
| 0 | Configuración global, tema (oscuro/claro), tokens de diseño, estilos base | `frontend/src/app/globals.css` · `frontend/src/components/ThemeProvider.tsx` · `frontend/src/app/layout.tsx` | Design tokens (`--bg-main`, `--gold-*`, `--border`), `[data-theme="light"]`, clases `.atelier-card`, `.atelier-skeleton`, `.dropzone-atelier` |
| 1 | Layout raíz: TopBar (3 zonas), Drawer lateral (Cotizador), Footer | `frontend/src/app/sidebar-layout.tsx` · `frontend/src/components/Sidebar.tsx` · `frontend/src/components/ThemeProvider.tsx` | Header sticky, nav, "Subir Foto", toggle tema, "Cotizar"; drawer con cotizador; footer |
| 2 | Página raíz `/` | `frontend/src/app/page.tsx` | Solo hace `redirect("/search")` |
| 3 | Buscador visual `/search` | `frontend/src/app/search/page.tsx` · `frontend/src/components/Skeleton.tsx` · `frontend/src/lib/api.ts` · `frontend/src/app/api/images/[filename]/route.ts` | Dropzone, drag&drop, `Ctrl+V`, presets de muestra, caja de revisión de consulta, skeletons, grilla de resultados, tarjetas, 3 modales |
| 4 | Catálogo oficial `/catalog` | `frontend/src/app/catalog/page.tsx` · `frontend/src/lib/catalog.ts` · `frontend/src/lib/countries.ts` | Grilla de 8 productos `ATL-*`, buscador, filtros por colección, specs, acciones "Buscar Similares" / "Cotizar" |
| 5 | Muestrario de casos `/eval` | `frontend/src/app/eval/page.tsx` | Casos demo hardcodeados (`caso_tienda`, `caso_redes`, `caso_clasico`, `caso_sublimacion`) |
| 6 | Proxy de imágenes del catálogo | `frontend/src/app/api/images/[filename]/route.ts` | Resuelve nombre de archivo → ruta (4 directorios + fallback `.jpg`), validación de path traversal |
| 7 | Datos del catálogo / contrato de API | `frontend/src/lib/catalog.ts` · `frontend/src/lib/countries.ts` · `frontend/src/lib/types.ts` · `frontend/src/lib/api.ts` | `CATALOG_JERSEYS`, `ApiResult`, `HealthInfo`, `SearchResult` |

---

## 3. Detalle por sección visual

### 3.1 Tema global (oscuro / claro)
- **Archivo que altera:** `frontend/src/app/globals.css`
- **Archivo que altera:** `frontend/src/components/ThemeProvider.tsx`
- **Archivo que altera:** `frontend/src/app/layout.tsx`
- **Qué cambia:** tokens CSS (`--bg-main`, `--bg-surface`, `--gold-500: #C5A880`, `--border`, `--success-*`), tema oscuro por defecto y tema claro vía `[data-theme="light"]`, fondo con degradado radial sutil, tipografía, scrollbar, clases compuestas (`.atelier-card`, `.atelier-skeleton`, `.dropzone-atelier`).

### 3.2 Layout raíz: TopBar + Drawer + Footer
- **Archivo que altera:** `frontend/src/app/sidebar-layout.tsx`
- **Archivo que altera:** `frontend/src/components/Sidebar.tsx`
- **Qué cambia:** TopBar sticky de 3 zonas (wordmark "Atelier Sublitex", nav Buscador/Catálogo/Muestrario, CTA "Subir Foto" + toggle tema + botón "Cotizar"); contenedor `max-w-[1360px]`; footer con enlaces y CTA de cotización.

### 3.3 Página raíz `/`
- **Archivo que altera:** `frontend/src/app/page.tsx`
- **Qué cambia:** redirección a `/search`.

### 3.4 Buscador `/search` (la sección más compleja)
- **Archivo que altera:** `frontend/src/app/search/page.tsx` — orquestador visual completo:
  - Dropzone (clic, drag & drop, `Ctrl+V`).
  - Validación de tipo (JPG/PNG/WEBP).
  - Presets de muestra (`handleSelectSample`, 6 camisetas).
  - Caja de revisión de la consulta.
  - `ResultCardSkeleton` + grilla de resultados.
  - Ranking `#n`, código, `score_reranking ?? score`, etiqueta de coincidencia exacta/Alta similitud/Alternativa, país, liga, temporada, corte, tejido, precio, plazo.
  - **3 modales:** comparador, ficha técnica, cotización.
- **Archivo que altera:** `frontend/src/components/Skeleton.tsx` — `Skeleton` y `ResultCardSkeleton`.
- **Archivo que altera:** `frontend/src/lib/api.ts` — fetch a la API, validaciones cliente, fallback "modo demo" si la API no responde (oculta caídas; riesgo documentado).
- **Archivo que altera:** `frontend/src/app/api/images/[filename]/route.ts` — proxy para imágenes.

### 3.5 Catálogo `/catalog`
- **Archivo que altera:** `frontend/src/app/catalog/page.tsx` — grilla de 8 productos, buscador, filtros por colección, modal de specs.
- **Archivo que altera:** `frontend/src/lib/catalog.ts` — datos `CATALOG_JERSEYS` (equipo, liga, temporada, colores, precios, plazo, corte, `sublimationSpecs`).
- **Archivo que altera:** `frontend/src/lib/countries.ts` — datos de países/ligas.

### 3.6 Muestrario `/eval`
- **Archivo que altera:** `frontend/src/app/eval/page.tsx` — página estática con 4 casos demo (`caso_tienda`, `caso_redes`, `caso_clasico`, `caso_sublimacion`) y % de similitud fijos.

### 3.7 Proxy de imágenes y assets
- **Archivo que altera:** `frontend/src/app/api/images/[filename]/route.ts`
- **Carpetas:** `frontend/public/images/`, `frontend/src/assets/images/`

---

## 4. Tabla resumen rápida (para referencia)

| Sección | Archivo principal |
|---|---|
| Tema / tokens / estilos globales | `src/app/globals.css` |
| Toggle tema / provider | `src/components/ThemeProvider.tsx` |
| TopBar / Footer / layout | `src/app/sidebar-layout.tsx` |
| Drawer cotizador | `src/components/Sidebar.tsx` |
| Home `/` | `src/app/page.tsx` |
| Buscador `/search` + tarjetas + modales | `src/app/search/page.tsx`, `src/components/Skeleton.tsx` |
| Cliente API / fallback demo | `src/lib/api.ts` |
| Proxy imágenes | `src/app/api/images/[filename]/route.ts` |
| Catálogo `/catalog` | `src/app/catalog/page.tsx`, `src/lib/catalog.ts` |
| Muestrario `/eval` | `src/app/eval/page.tsx` |

---

## 5. Cambios visuales recientes (contexto: "mejora del UI")

- **2026-10-19:** Rediseño a identidad **Atelier Sublitex** (fondo oscuro + oro, tema claro, top bar nuevo, resultados enriquecidos, catálogo nuevo, cotizador, 6 botones de WhatsApp, `/eval` degradado a muestrario).
- Archivos clave del cambio: `src/app/globals.css`, `src/app/sidebar-layout.tsx`, `src/app/search/page.tsx`, `src/app/catalog/page.tsx`, `src/app/eval/page.tsx`, `src/components/Sidebar.tsx`, `src/components/Icons.tsx`, `src/components/Skeleton.tsx`, `src/lib/catalog.ts`, `src/lib/api.ts`.

Detalle completo: **`mejora del UI.md`** (raíz del repo).

---

## 6. Pendientes que implican cambios visuales

1. Fallback simulado en `src/lib/api.ts` → mover a variable de entorno (`NEXT_PUBLIC_DEMO_MODE`).
2. `/eval` perdió el evaluador de métricas del Hito 2 → restaurar en otra ruta si aplica.
3. WhatsApp: fijar número comercial real.
4. Eliminar assets duplicados (`public/images/` vs `src/assets/images/`).
5. Definir cuál es la interfaz oficial: `app.py` (Streamlit) o la app Next.js.

---

## 7. Cómo verificar

```bash
source .venv/bin/activate.fish        # Linux/Arch
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

cd frontend
npm run dev                            # http://localhost:3000
```

Flujo de verificación visual rápido: levantar API + frontend, abrir `/search`, probar un preset de muestra, alternar tema, abrir catálogo y cotizador.
