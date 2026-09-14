# Frontend Next.js — Búsqueda Visual de Camisetas

Interfaz web moderna del **RAG visual de camisetas deportivas** construida con
**[Next.js](https://nextjs.org) (App Router) + React 19 + TypeScript**.

Consume la API FastAPI (`http://localhost:8000`) y ofrece tres pantallas:

| Ruta | Pantalla | Qué hace |
|---|---|---|
| `/` | **Búsqueda visual** | Sube una imagen, la API devuelve el Top 5 y puedes calificar cada resultado con **✅ Acierto / 👍 Sirve / ❌ No sirve**. Los veredictos se guardan en la API (CSV) y las imágenes marcadas "No sirve" **no vuelven a aparecer aunque recargues**. |
| `/evaluacion` | **Evaluador del buscador** | Recorre los casos de prueba, muestra la consulta + el Top 5 y permite calificar los 5 resultados. Botón **Siguiente →** y contador **"Caso X de Y"**. Cada clic se guarda al instante en `evaluador/resultados.csv`. |
| `/search10` | **Search-10 · Entrenar** | Bucle de entrenamiento con feedback sobre `proyectoA/Search-10/`: elige una consulta, ranking real, y califica **✅ Correcto / 👍 Sirve / ❌ Incorrecto**. Lo marcado Incorrecto queda **excluido de forma persistente** para esa consulta. **Usa su propio backend en `:8400`** (ver §5). |

> **`/search10` NO usa la API `:8000`.** Tiene su backend dedicado:
> `python -m uvicorn backend.main:app --port 8400` desde `proyectoA/`
> (ver `proyectoA/README.md`).

---

## 1 · Requisitos previos

- **Node.js 20.9+** (requerido por Next.js 16; probado con Node 20/22). npm se incluye con Node.
- La **API FastAPI corriendo** en `http://localhost:8000`
  (`python -m uvicorn api.main:app --port 8000` desde la raíz del repositorio).
  Sin la API, la interfaz se abre pero las búsquedas fallan.

Verifica Node y npm:

```bash
node -v   # v20.9.0 o mayor
npm -v
```

### 1.1 · Instalar Node.js por sistema operativo

**Linux (Debian/Ubuntu) con nvm (recomendado):**

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
# cerrar y reabrir la terminal, luego:
nvm install 20
nvm use 20
```

**Linux — alternativa con apt:**

```bash
sudo apt update
sudo apt install -y nodejs npm
```

> ⚠️ Los repositorios de Ubuntu <24.10 y Debian estable traen Node **18**, que no
> cumple el requisito de Next.js 16 (>=20.9). Verifica con `node -v` y, si hace
> falta, usa **nvm** (arriba) o el repositorio [NodeSource](https://github.com/nodesource/distributions).

**Linux — Arch / Manjaro / EndeavourOS (pacman):**

```bash
sudo pacman -Syu nodejs npm
```

> Arch trae las últimas versiones de Node/npm en sus repositorios oficiales, así
> que cumple el requisito de Next.js 16 sin pasos extra. Verifica con `node -v`.

**Windows:**

1. Descarga el instalador LTS desde <https://nodejs.org> (`node-v20.x.x-x64.msi`).
2. Ejecuta el `.msi` y acepta los pasos por defecto (incluye npm).
3. Verifica en PowerShell o CMD: `node -v` y `npm -v`.

**macOS — con Homebrew (recomendado):**

```bash
brew install node@20
```

**macOS — alternativa con nvm:**

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
nvm install 20
nvm use 20
```

---

## 2 · Instalación

Los comandos son idénticos en los tres sistemas: abre una terminal en la
carpeta `proyectoA/frontend-next/` del proyecto y ejecuta:

```bash
cd proyectoA/frontend-next
npm install
```

Instala todas las dependencias de `package.json` (Next.js, React, TypeScript,
ESLint) y crea `node_modules/` + `package-lock.json`.

> No uses `npm install` a nivel raíz del repositorio (ahí viven las
> dependencias de Python de la API).

---

## 3 · Cómo correr el programa

> 💡 **Página `/search10`:** usa un backend **propio** en el puerto **8400**
> (`cd /home/satanic/RAG-V2/proyectoA && ../venv/bin/python -m uvicorn backend.main:app --port 8400`),
> no la API de `:8000`. Ver `proyectoA/README.md`.

> ### ⚠️ MUY IMPORTANTE: `npm run dev` NO es suficiente
>
> `npm run dev` solo abre la interfaz en **http://localhost:3000**, pero **NO
> levanta la API**. La búsqueda visual depende al 100% de la **API FastAPI** en
> `http://localhost:8000`: si la API no está corriendo, la página se abre pero
> cada búsqueda falla (no aparece el Top 5).
>
> **Pasos correctos (dos terminales):**
>
> ```bash
> # Terminal 1 — la API (desde la RAIZ del repositorio, NO en frontend-next/)
> cd /home/satanic/RAG-V2
> python -m uvicorn api.main:app --port 8000
>
> # Terminal 2 — la interfaz
> cd /home/satanic/RAG-V2/proyectoA/frontend-next
> npm run dev
> ```
>
> **Antes de buscar, verifica que la API responde:**
>
> ```bash
> curl http://localhost:8000/health
> # debe devolver JSON con {"status":"ok", ...} — si no, la búsqueda fallará.
> ```

Los comandos de **Next.js son iguales en Linux, Windows y macOS** (también en
PowerShell o CMD de Windows).

### 3.0 · Comprobar el estado (qué probar para saber que todo funciona)

1. `curl http://localhost:8000/health` → la API responde **ok**.
2. Abre **http://localhost:3000** → la página carga.
3. Sube una imagen y pulsa buscar → aparece el **Top 5**. Si aquí falla, la API
   no está corriendo (revisa la terminal 1).

### 3.1 · Modo desarrollo (recomendado para trabajar)

```bash
npm run dev
```

Abre **http://localhost:3000** en tu navegador. Los cambios a los archivos de
`app/` se reflejan al instante (hot reload). Recuerda: la API desde la raíz del
repositorio (`python -m uvicorn api.main:app --port 8000`) debe estar corriendo.

### 3.2 · Modo producción (build + servidor)

```bash
npm run build      # compila y optimiza la app en .next/
npm run start      # sirve la build en http://localhost:3000
```

### 3.3 · Lint y tipos

```bash
npm run lint       # ESLint (Next.js config)
npx tsc --noEmit   # revisión de tipos TypeScript
```

### 3.4 · Puertos y configuración

| Elección | Dónde |
|---|---|
| Puerto del frontend | 3000 (por defecto de Next) |
| URL de la API | `API_URL` al inicio de `app/page.tsx` y `app/evaluacion/page.tsx` (`http://localhost:8000`) |

Si tu API corre en otro host/puerto, cambia `API_URL` en ambos archivos y
reinicies `npm run dev`.

> **Windows (PowerShell):** si Next pide permisos de red, acepta el aviso del
> firewall; si el puerto 3000 está ocupado, Next te ofrece usar el 3001.

---

## 4 · Estructura del proyecto (árbol)

```text
proyectoA/frontend-next/
├── app/                        # App Router de Next.js
│   ├── layout.tsx              # Layout raíz (fuente Geist + globals.css)
│   ├── globals.css             # Estilos globales y de la página de búsqueda
│   ├── page.module.css         # CSS residual de create-next-app (solo intro)
│   ├── page.tsx                # 🏠 Página principal: búsqueda + Top 5 + botones Acierto/Sirve/No sirve
│   ├── evaluacion/
│   │   ├── page.tsx            # 🏠 Página del evaluador: casos, Top 5 por caso, Siguiente, contador
│   │   └── evaluacion.css      # Estilos del evaluador
│   ├── search10/
│   │   ├── page.tsx            # 🏠 Search-10 · Entrenar: ranking real + feedback persistente (backend :8400)
│   │   └── search10.css        # Estilos de la vista de entrenamiento
│   └── favicon.ico
├── public/                     # SVGs estáticos de create-next-app
├── next.config.ts              # Config de Next (reactCompiler: true)
├── tsconfig.json               # Configuración de TypeScript
├── eslint.config.mjs           # Configuración de ESLint
├── package.json                # Dependencias y scripts (dev/build/start/lint)
└── .gitignore

# Backend que consume el frontend (raíz del repositorio)
api/
├── main.py                     # FastAPI: POST /search/image, /search/image/v2, GET /health
├── evaluacion.py               # Verdictos: POST/GET /evaluacion/* (guardar, estado, veredictos)
├── search_engine.py            # Búsqueda por embeddings (Hito 1)
├── search_engine_hito2.py      # Recuperación amplia + reranking (Hito 2)
├── preprocesar_consulta.py     # Sala 2: prepara la imagen de consulta
└── descriptores_visuales.py    # Descriptores HSV/estructura para el reranking

evaluador/
├── casos.csv                   # Def. de casos: caso, id_correcto, tipo
├── resultados.csv              # Cada clic guarda aquí (persistencia real)
├── completados.json            # Casos terminados (no vuelven a aparecer)
├── calcular.py                 # Métricas: Top 1, Top 5, Utilidad (total y por tipo)
└── README.md                   # Guía del evaluador

# Backend autocontenido del módulo Search-10 (puerto 8400, NO toca api/)
proyectoA/backend/
└── main.py                     # POST /search10/buscar, /feedback, /feedback/limpiar + static
```

---

## 5 · Lo que se hizo (funcionalidades)

1. **Búsqueda visual por imagen** — `app/page.tsx` sube la foto, llama a
   `POST /search/image` (`modo=auto`) y pinta el Top 5 (imagen, nombre, id,
   proveedor, score + barra de score).
2. **Calificación en vivo (✅ Acierto / 👍 Sirve / ❌ No sirve)** — cada
   tarjeta tiene 3 botones; al pulsarlos se guarda el veredicto (Caso / Posición
   / Id resultado / Score / Juicio) mediante `POST /evaluacion/guardar`.
3. **Filtrado persistente de "No sirve"** — la página carga los veredictos con
   `GET /evaluacion/veredictos` y oculta para siempre (también tras recargar) los
   productos marcados "No sirve". Cache local en `localStorage`.
4. **Evaluador del buscador** — `app/evaluacion/page.tsx` recorre los casos de
   `proyectoA/Search-10` (o `evaluador/casos/`), consulta la API por cada uno y
   permite calificar los 5 resultados con definiciones en pantalla.
5. **Navegación entre casos** — botón **Siguiente →** + contador
   **"Caso X de Y"** con avance global; un caso avanza solo cuando se califican
   todos sus resultados.
6. **Persistencia real** — cada clic escribe una fila en
   `evaluador/resultados.csv` al instante (sobrevive al cierre del navegador).
7. **Search-10 · Entrenar (`/search10`)** — bucle de entrenamiento con backend
   propio (`proyectoA/backend/main.py`, puerto **8400**): lista las 14 consultas
   de `proyectoA/Search-10/`, lanza el ranking real en vivo, y cada resultado se
   califica con **✅ Correcto / 👍 Sirve / ❌ Incorrecto**. Lo marcado Incorrecto
   queda **excluido de forma persistente** (`.feedback/feedback.json`) y la
   re-búsqueda lo omite rellenando con la siguiente alternativa válida.

---

## 6 · Anatomía de un buen README

Este documento sigue la estructura estándar de un README de proyecto. Si
quieres replicar el formato en otro módulo, debe incluir:

1. **Título + descripción** — qué es y para qué sirve (1-2 líneas).
2. **Requisitos previos** — versiones de runtime/herramientas necesarias.
3. **Instalación** — pasos exactos para dejar el entorno listo.
4. **Cómo correr** — comandos de desarrollo, producción y salidas esperadas.
5. **Estructura del proyecto** — árbol de archivos para orientarse rápido.
6. **Funcionalidades** — qué se construyó y cómo.
7. **Referencias** — endpoints de la API, rutas o documentación relacionada.

---

## Referencias

- [Next.js docs](https://nextjs.org/docs) — framework.
- Repositorio raíz: `api/` (FastAPI), `evaluador/` (evaluación y métricas),
  `README.md` (guía general del proyecto RAG).