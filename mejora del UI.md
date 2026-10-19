# Mejora de UI de la página — nuevo interfaz "Atelier Sublitex"

> Fecha del documento: 2026-10-19
> Alcance: solo los **cambios de la interfaz web** (`frontend/`, app Next.js).
> Parte 1 = para personas · Parte 2 = para la IA.

---

# Parte 1 — Qué cambió en la página (para personas)

## En una frase

La página ahora se ve como una tienda de camisetas personalizadas de lujo:
antes era un buscador técnico, ahora es un **catálogo con precios, un
cotizador y botones para escribir por WhatsApp**.

## Lo que notas al usarla

- **Se ve distinta y elegante:** fondo oscuro con detalles en oro (y se puede
  pasar a fondo claro con el botón de sol/luna arriba).
- **Arriba hay un menú nuevo:** logo "Atelier Sublitex", links a *Buscar*,
  *Catálogo* y *Muestrario*, y un botón destacado **"Subir Foto"**.
- **Buscar es más fácil:** además de elegir un archivo, ahora puedes
  **arrastrar la foto** hasta la página o **pegarla con `Ctrl+V`**. También hay
  6 camisetas de ejemplo que se buscan con un solo clic.
- **Los resultados dan más información:** cada camiseta muestra el lugar en el
  ranking, el **% de similitud**, si es coincidencia exacta o solo una
  alternativa, de qué país/liga es, el corte, el tejido, **el precio** y en cuántos
  días se entrega. Además hay botones para **comparar tu foto con la del
  catálogo** y ver la ficha técnica.
- **Ahora hay catálogo:** página nueva con 8 camisetas, buscador por equipo o
  país, filtros por colección y ficha con precios (sueltas, en equipo de 12 o
  liga de 30).
- **Hay un cotizador:** un panel lateral que se abre con "Cotizar" donde eliges
  cantidad (1 a 60), tejido y cuello, y te calcula el subtotal al instante.
- **Directo a WhatsApp (lo nuevo principal):** hay **6 botones de WhatsApp**
  (en el cotizador, en el catálogo y en los resultados de búsqueda) que ya te
  arman el mensaje con la cantidad, el modelo y los precios — solo falta apretar
  enviar. Hoy el mensaje **no tiene un número fijo**: WhatsApp te deja elegir a
  quién mandarlo.
- **Cambia una página:** `/eval` ya **no es el evaluador de métricas**; ahora es
  una página de muestras con 4 casos de demostración. ⚠️ Si seguís necesitando
  evaluar resultados, esa herramienta se perdió de la interfaz (ver Parte 2).

## Antes → Después

| Aspecto | Antes | Después |
| --- | --- | --- |
| Estilo | Interfaz técnica genérica | Identidad "Atelier Sublitex" (lujo deportivo), tema oscuro/claro |
| Panel lateral | Estado de la API (URL, health) | Cotizador con precios y WhatsApp |
| Subir imagen | Solo elegir archivo | Arrastrar, `Ctrl+V` o elegir archivo |
| Catálogo | No existía | `/catalog` con 8 productos, buscador y filtros |
| Cotización | Inexistente | 6 botones de WhatsApp con mensaje pre-armado |
| Resultados | Tarjetas básicas | Ranking, % de similitud, etiqueta, precio, plazo + 3 modales |
| `/eval` | Evaluador con métricas y CSV | Muestrario de 4 casos ⚠️ |

---

# Parte 2 — Detalle técnico (para la IA)

## 1. Ubicación del código

- Fuente de la UI: rama **`sala-5`**, commit **`1b863a2f`** (integrado en `main`
  vía merge `643dcebd`, PR #2).
- En `main` **falta `frontend/src/`** (solo `.gitignore`, `next-env.d.ts`,
  `app.py`, caché `.next/`). Restaurar con:

```bash
git checkout 1b863a2f -- frontend/src frontend/public frontend/package.json \
  frontend/next.config.ts frontend/eslint.config.mjs frontend/tsconfig.json
```

- ⚠️ El merge trajo ~830 archivos de `frontend/.next/` a Git: sacarlos con
  `git rm -r --cached frontend/.next`.
- `frontend/app.py` (Streamlit, interfaz anterior) sigue en el repo.

## 2. Rutas y layout

- `/` → `redirect("/search")`.
- Layout en `src/app/sidebar-layout.tsx`: barra superior de 3 zonas (logo,
  links Buscar/Catálogo/Muestrario, "Subir Foto" + toggle de tema + "Cotizar"),
  contenedor `max-w-[1360px]` y footer.
- `src/app/layout.tsx`: `metadata` = "Aimari RAG Visual - Búsqueda de Camisetas"
  + `openGraph`.

## 3. Pantallas

| Archivo | Qué contiene |
| --- | --- |
| `src/app/search/page.tsx` (+958/-643) | Dropzone (clic, drag&drop, `Ctrl+V`), validación de tipo (JPG/PNG/WEBP), 6 presets (`handleSelectSample`), caja de revisión de la consulta, `ResultCardSkeleton`, grilla de resultados (ranking `#n`, código, `score_reranking ?? score`, etiqueta Coincidencia exacta ≥95% / Alta similitud ≥85% / Alternativa de diseño, país, liga, temporada, corte, tejido, precio, plazo) y 3 modales (comparador, ficha técnica, cotización). Usa `NEXT_PUBLIC_API_URL` con fallback `http://localhost:8000`. |
| `src/app/catalog/page.tsx` (nuevo) | Grilla de 8 productos `ATL-*`, buscador por nombre/equipo/país, filtros por colección (Bespoke Atelier, Selecciones, Clubes Élite, Heritage Retro, Kits de Competición), modal de specs (tejido, cuello, manga, impresión; precios individual / equipo 12+ / liga 30+) y acciones "Buscar Similares" + "Cotizar". |
| `src/app/eval/page.tsx` (+168/-879) | Dejó de ser el evaluador del Hito 2. Ahora es página estática con 4 casos hardcodeados (`caso_tienda`, `caso_redes`, `caso_clasico`, `caso_sublimacion`) y % de similitud fijo (97.8–99.2%). **Código previo:** `git show 1b863a2f~1:frontend/src/app/eval/page.tsx`. |
| `src/app/globals.css` (+225/-774) | Design tokens (`--bg-main`, `--gold-500: #C5A880`, `--border`, `--success-*`...), oscuro por defecto, claro con `[data-theme="light"]`, clases `.atelier-card`, `.atelier-skeleton`, `.dropzone-atelier` (+ `.is-active`). |

## 4. Componentes y librería

| Archivo | Qué es |
| --- | --- |
| `src/components/Sidebar.tsx` (+287/-672) | Cotizador: slider de cantidad 1–60, precios unitarios S/ 48 / 38 / 32, subtotal, tejido, cuello ("Cuello en V Anatómico" / "Polo Camisero" / "Redondo Match"), toggles de personalización y CTA WhatsApp. Reemplazó al panel de estado de la API. |
| `src/components/Icons.tsx` (nuevo) | Wrapper tipado de `lucide-react`; exponer vía objeto `Icons` (~45 íconos), no importar íconos directamente. |
| `src/components/Skeleton.tsx` (nuevo) | `Skeleton`, `ResultCardSkeleton`. |
| `src/components/ThemeProvider.tsx` | Sin cambios; lo consume `sidebar-layout.tsx`. |
| `src/lib/catalog.ts` (nuevo) | `CATALOG_JERSEYS`: 8 productos con equipo, liga, temporada, colores+hex, imagen, precios, plazo, corte y `sublimationSpecs`. **No** es `data/products.csv`. Se usa en presets, `/catalog` y el fallback de `api.ts`. |
| `src/lib/countries.ts`, `src/lib/types.ts` | Sin cambios. El contrato de la API no cambió (`ApiResult.nombre`, `imagen`, `url`, `score`, `score_reranking`, ...). |
| `src/app/api/images/[filename]/route.ts` | Busca en 4 directorios (`public/images`, `public`, `src/assets/images`, `../data/images_normalized`) con fallback `.jpg`; valida path traversal con `path.basename`; `params` es `Promise<>` (Next 16). |

## 5. WhatsApp

- 6 `href = "https://wa.me/?text=" + encodeURIComponent(...)`, **sin número**:
  1 en `components/Sidebar.tsx`, 2 en `app/catalog/page.tsx`, 3 en
  `app/search/page.tsx`.
- Para número fijo: `https://wa.me/<codigo_pais><numero>?text=...`.

## 6. `src/lib/api.ts` — fallback "modo demo" ⚠️

- `healthCheck` / `searchImage` con `AbortSignal.timeout(2500)` (antes 6000 ms y
  180 000 ms).
- Si la API no responde: **no muestra error**, devuelve datos simulados
  (`products: 1840`, `model: "Fashion-CLIP + YOLO (Catálogo Sublitex)"`,
  scores heurísticos por nombre de archivo, preprocesamiento ficticio
  `"yolo-v8-jersey-detector"`, 600 ms simulados).
- `searchImage` agrega parámetro `modelo` (default `"fusion"`).
- **Riesgo:** oculta caídas de la API y muestra resultados inventados; para
  evaluar hay que desactivarlo (p. ej. flag `NEXT_PUBLIC_DEMO_MODE`).

## 7. Config y dependencias

- `package.json`: `dev`/`start` → `next dev|start -p 3000 -H 0.0.0.0`; nuevas
  deps **`lucide-react@^1.58.0`** (usada) y **`motion@^14.3.0`** (**sin uso**:
  eliminar o usar).
- `next.config.ts`: `output: "standalone"`.
- `eslint.config.mjs`: off para `react-hooks/set-state-in-effect` y
  `@next/next/no-img-element`; `no-unused-vars` como warn ignorando `_`.
- Assets duplicados: 9 fotos en `public/images/` y otras 9 con timestamp en
  `src/assets/images/` → quedarse con un solo directorio.
- Sin cambios para el backend: índices y `products.csv` intactos.

## 8. Pendientes conocidos

1. `/eval` perdió el evaluador del Hito 2 (AGENTS.md §8: mínimo 50 consultas,
   comparación Hito 1 vs Hito 2) → restaurarlo en otra ruta si aplica.
2. Fallback simulado trasladarlo a variable de entorno.
3. WhatsApp: fijar número si es línea comercial real.
4. Sacar `.next/` de Git y restaurar `frontend/src` en `main`.
5. Definir cuál es la interfaz oficial: `app.py` (Streamlit) o la app Next.js.
