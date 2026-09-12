# AI_LOG.md — Evaluador (Ficha 03-A)

Registro de prompts y decisiones de IA utilizadas en la construccion del Evaluador.
Ambos integrantes deben poder explicar cada decision documentada aqui.

---

## Fecha: 2026-09-11

### Prompt 1 — Analisis de requisitos

**Prompt usado**: "Analiza la Ficha 03-A del grupo A y genera un plan de trabajo que divida las tareas entre dos integrantes: uno para backend y datos, otro para frontend y experiencia de usuario. Incluye estructura de carpetas, contrato de datos, y endpoints necesarios."

**Que se genero**: Plan de trabajo con division clara de responsabilidades:
- Integrante 1 (backend): server.py, metricas.py, casos.csv, README.md
- Integrante 2 (frontend): index.html, app.js, styles.css

### Prompt 2 — Implementacion del backend

**Prompt usado**: "Implementa el backend del evaluador en Python con FastAPI. Debe exponer los siguientes endpoints: listar casos, obtener caso con resultados de la API principal, guardar juicios en CSV, calcular estadisticas. Usa el contrato de datos: casos.csv con columnas caso,id_correcto,tipo y resultados.csv con columnas caso,id_correcto,posicion,id_resultado,score,juicio,quien,fecha. El backend solo consume la API principal, no busca nada localmente."

**Que se implemento**:
- `server.py`: FastAPI con 10 endpoints
- `metricas.py`: script standalone de metricas
- `casos/casos.csv`: 10 casos de prueba
- `README.md`: documentacion completa

### Decisiones de arquitectura (Backend)

1. **Backend con FastAPI**: se eligio por consistencia con la API principal del proyecto. Permite CORS automatico, validacion de tipos, y documentacion en /docs.

2. **Proxy a la API**: el evaluador NO busca nada directamente. Llama a `POST /search/image` de la API principal para obtener los resultados. Esto garantiza que siempre se mida el motor real.

3. **Guardado inmediato**: cada clic se guarda con `csv.DictWriter` en modo append (`"a"`). Si el navegador se cierra, lo que se guardo sigue en disco.

4. **Metricas en dos sitios**: el endpoint `/api/estadisticas` calcula en tiempo real, y `metricas.py` es un script standalone que puede correrse sin el servidor.

---

## Fecha: 2026-09-12

### Prompt 3 — Verificacion del frontend del compañero

**Prompt usado**: "Analiza los archivos frontend/index.html, frontend/app.js y frontend/styles.css que construyo el segundo integrante. Verifica que se comuniquen correctamente con los endpoints del backend server.py. Identifica cualquier desajuste en URLs de endpoints, formato de envio de datos, o nombres de campos."

**Que se encontro**: 7 errores que impedian el funcionamiento:
- Endpoint incorrecto para guardar juicios
- Formato de envio incompatible (JSON vs Form Data)
- Nombres de campos diferentes
- Endpoint inexistente
- Carga incorrecta de resultados
- URLs de imagenes rotas
- Metricas consultadas en endpoint equivocado

### Prompt 4 — Correccion del frontend con minimos cambios

**Prompt usado**: "Corrige los errores encontrados en el frontend realizando los cambios minimos necesarios. Manten la estructura y estilo que ya existia. Solo ajusta la logica de comunicacion con el backend para que funcione correctamente."

**Correcciones realizadas**:

| Archivo | Cambio | Justificacion |
|---------|--------|---------------|
| `app.js` | Endpoint `/api/guardar-juicio` → `/api/juicios` | Alineacion con el backend existente |
| `app.js` | `JSON.stringify` → `URLSearchParams` | El backend espera form-data |
| `app.js` | Campo `who` → `quien` | Alineacion de nombres de campos |
| `app.js` | Eliminar `POST /api/siguiente-caso` | Endpoint inexistente |
| `app.js` | Cargar resultados con `GET /api/casos/{n}` | El endpoint `/api/casos` solo devuelve metadata |
| `app.js` | URL de imagenes → `/api/imagen/{res.imagen}` | Las imagenes del catalogo estan en `data/images_normalized/` |
| `server.py` | `FRONTEND_DIR` apunta a `evaluador/frontend/` | Correccion de ruta estatica |

### Prompt 5 — Adicion de endpoints para imagenes

**Prompt usado**: "Las imagenes de consulta y del catalogo no se estan sirviendo correctamente. Agrega los endpoints necesarios en server.py para servir tanto las imagenes de consulta (ubicadas en evaluador/casos/) como las imagenes del catalogo (ubicadas en data/images_normalized/)."

**Endpoints agregados**:
- `GET /api/imagen/{nombre}`: sirve imagenes del catalogo con busqueda multi-extension
- `GET /api/caso-imagen/{nombre}`: sirve fotos de consulta de los casos

### Prompt 6 — Boton Siguiente dinamico

**Prompt usado**: "El boton Siguiente solo se habilita cuando hay 5 clics, pero la API a veces devuelve menos de 5 resultados. Modifica la logica para que el boton se habilite cuando se evaluen todos los resultados visibles, no siempre 5."

**Solucion**: Se agrego la variable `totalResultadosActual` que se actualiza con la cantidad real de resultados devueltos por la API. El boton verifica contra esa variable en vez de un valor fijo.

### Prompt 7 — Imagenes en blanco

**Prompt使用权**: "Algunas imagenes de resultados aparecen en blanco en el navegador. Verifica que todas las imagenes referenciadas por la API existan en data/images_normalized/ y corrige el endpoint para que las encuentre."

**Causa**: la API del buscador devuelve nombres como `AIM-P254-033.png` pero el archivo real es `AIM-P254-033.jpg`.

**Solucion**: el endpoint `/api/imagen/{nombre}` ahora busca automaticamente con otras extensiones (`.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`) si el nombre exacto no existe.

### Prompt 8 — Retomar progreso tras cerrar navegador

**Prompt usado**: "Implementa la funcionalidad de retomar el progreso cuando se cierra y reabre el navegador. Al cargar la pagina, debe buscar en resultados.csv que casos ya tienen juicios y continuar desde el primer caso pendiente."

**Solucion**: en `cargarCasoActual()`, se piden los resultados existentes (`GET /api/resultados`), se cuentan los juicios por caso, y se busca el primer caso que no tenga todos sus juicios para continuar desde ahi.

### Decisiones de arquitectura (Frontend)

1. **HTML/CSS/JS puro**: se uso la tecnologia que el segundo integrante ya conocia, sin frameworks complejos.

2. **Criterios en pantalla**: los botones y sus definiciones estan escritos en el HTML para que quien evaluce los tenga a la vista.

3. **Guardado por clic**: cada boton envia `POST /api/juicios` inmediatamente. No se espera a que termine el caso.

4. **Retomar progreso**: al cerrar y reabrir el navegador, se buscan los casos ya evaluados en el CSV y se salta ahi.

### Validaciones

- `server.py`: verificado con `python -m py_compile` (sin errores)
- `app.js`: verificado con `node -c` (sin errores)
- Todos los endpoints probados con peticiones HTTP:
  - `GET /` → 200 OK
  - `GET /api/casos` → 200 OK (10 casos)
  - `GET /api/casos/1` → 200 OK (5 resultados)
  - `GET /api/caso-imagen/caso-001.jpg` → 200 OK
  - `GET /api/imagen/AIM-P170-053.jpg` → 200 OK
  - `POST /api/juicios` → 200 OK (guarda en CSV)
  - `GET /api/resultados` → 200 OK
  - `GET /api/estadisticas` → 200 OK
  - `GET /health` → 200 OK
