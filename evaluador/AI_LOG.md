# AI_LOG.md — Evaluador (Ficha 03-A)

> Registro de asistencia de IA utilizada en la construccion del Evaluador.
> Ambos integrantes deben poder explicar cada decision documentada aqui.

## Fecha: 2026-09-11

### Prompt 1 - Analisis de requisitos y plan de trabajo

**Propósito:** Comprender la Ficha 03-A y dividir el trabajo entre dos integrantes.
**Resultado:** Plan de trabajo con responsabilidades claras: Integrante 1 (backend: `server.py`, `metricas.py`, `casos/casos.csv`, `README.md`), Integrante 2 (frontend: `index.html`, `app.js`, `styles.css`).

### Prompt 2 - Implementacion del backend

**Propósito:** Crear el servidor FastAPI que sirve de proxy entre el frontend y la API del buscador.
**Resultado:** `server.py` con 10 endpoints (listar casos, obtener caso con resultados, guardar juicios, estadisticas, servir imagenes, proxy de health). `metricas.py` como script standalone que lee `resultados.csv` y calcula Top 1, Top 5 y Utilidad. `casos/casos.csv` con 10 casos de prueba.

---

## Fecha: 2026-09-12

### Prompt 3 - Verificacion del frontend del compañero

**Propósito:** Verificar que los archivos del frontend se comuniquen correctamente con los endpoints del backend.
**Resultado:** Se encontraron 7 errores que impedían el funcionamiento: endpoint `/api/guardar-juicio` no existente (cambiado a `/api/juicios`), envio de JSON en vez de form-data, campo `who` no coincidente (cambiado a `quien`), llamada a `/api/siguiente-caso` inexistente (eliminada), carga de resultados desde `/api/casos` (cambiado a `/api/casos/{n}`), URLs de imagenes incorrectas (corregidas a `/api/imagen/{res.imagen}`), y `FRONTEND_DIR` apuntando a ruta incorrecta en `server.py`.

### Prompt 4 - Endpoints para imagenes

**Propósito:** Las imagenes de consulta y del catalogo no se estaban sirviendo correctamente.
**Resultado:** Se agregaron dos endpoints: `GET /api/imagen/{nombre}` para imagenes del catalogo desde `data/images_normalized/` con busqueda multi-extension, y `GET /api/caso-imagen/{nombre}` para fotos de consulta desde `evaluador/casos/`.

### Prompt 5 - Boton Siguiente dinamico

**Propósito:** El boton "Siguiente" solo se habilitaba con 5 clics fijos, pero la API a veces devuelve menos de 5 resultados.
**Resultado:** Se agrego la variable `totalResultadosActual` que se actualiza con la cantidad real de resultados devueltos por la API. El boton verifica contra esa variable en vez de un numero fijo.

### Prompt 6 - Retomar progreso tras cerrar navegador

**Propósito:** Si el usuario cierra el navegador a mitad de la evaluacion, debe poder continuar donde quedo.
**Resultado:** En `cargarCasoActual()`, se piden los resultados existentes (`GET /api/resultados`), se cuentan los juicios por caso, y se busca el primer caso que no tenga todos sus juicios para continuar desde ahi.

---

## Fecha: 2026-09-14

### Prompt 7 - Correccion de tipos en casos.csv

**Propósito:** Los 10 casos tenian todos el tipo "persona", lo que hacia inutil el desglose por tipo de foto.
**Resultado:** Se redistribuyo la distribucion: casos 001-003 persona, 004-006 producto, 007-008 captura, 009-010 dificil.

### Prompt 8 - Mostrar nombre del diseno en resultados

**Propósito:** El frontend solo mostraba el ID de cada resultado, no el nombre. La Ficha pide "imagen, nombre y score".
**Resultado:** Se cambio `<h4>ID: ${res.id}</h4>` por `<h4>${res.nombre || res.id}</h4>` en el `innerHTML` de cada tarjeta.

### Prompt 9 - Campo "quien" editable

**Propósito:** El campo `quien` estaba hardcodeado como "Andres y Samir". Quien evalua debe poder escribir su nombre.
**Resultado:** Se agrego un `<input>` en el HTML con id `quien-input`, y se envia ese valor en cada juicio via `document.getElementById('quien-input').value`.

### Prompt 10 - Prevencion de juicios duplicados

**Propósito:** El usuario podia apretar el mismo boton multiples veces, creando filas duplicadas en `resultados.csv`.
**Resultado:** Se agrego la variable `juiciosEnviados` que registra que posiciones ya se enviaron al backend. Si ya se envio, solo se actualiza la seleccion visual sin hacer otro POST.

### Prompt 11 - Correccion de la logica de reanudacion

**Propósito:** La reanudacion mostraba la pantalla final cuando quedaban casos por evaluar.
**Resultado:** Se corrige para contar posiciones unicas usando `Set`, y se verifica contra el total real de resultados que devuelve la API (no contra 5 fijo).

### Prompt 12 - Anti-cache en el navegador

**Propósito:** El navegador guardaba versiones viejas de `app.js` y `styles.css`, causando que los cambios no se vieran.
**Resultado:** Query parameters `?v=3` en las referencias del HTML y middleware `NoCacheMiddleware` en `server.py` que agrega headers `Cache-Control: no-cache` a archivos `.js`, `.css` y `.html`.

### Prompt 13 - Mejora visual del evaluador

**Propósito:** Mejorar la apariencia del evaluador manteniendo la estructura del compañero, con toques sutiles del estilo RAG-V2.
**Resultado:** Gradientes sutiles en el fondo, texto del titulo con gradiente azul, progreso con forma de pastilla, tarjetas con bordes suaves y hover con sombra, botones con gradientes, pantalla final con tarjetas de metricas (Top 1, Top 5, Utilidad), tabla por tipo, y boton "Volver a empezar". Responsive: 5 columnas a 3 a 2 segun ancho de pantalla.
