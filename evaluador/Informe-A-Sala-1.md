# Evaluador del Buscador — Ficha 03-A

**Sublitex · Biblioteca visual · Ficha 03-A · Evaluador · Versión 1.0**

**Grupo A — Pareja:** Samir Ochoa y Andrés Quispe

**Estado:** ✅ Completado al 100%

---

## Objetivo

Construir la herramienta con la que una persona califica los resultados del buscador y el sistema saca el número. La herramienta no busca nada: le pregunta al buscador (API) y muestra lo que responde.

**Frase de validación:** «Una pantalla donde se ve una foto arriba, los cinco resultados del buscador abajo, y tres botones en cada resultado. Al final, un número.»

---

## Estado de avance

| Requisito (Ficha 03-A) | Estado | Ubicación |
|---|---|---|
| Pantalla con foto arriba, 5 resultados abajo | ✅ Hecho | `frontend/index.html` |
| Tres botones por resultado: Acierto / Sirve / No sirve | ✅ Hecho | `frontend/app.js` |
| Criterio de botones visible en la pantalla | ✅ Hecho | `frontend/index.html` (sección criterios) |
| Botón "Siguiente" para avanzar al siguiente caso | ✅ Hecho | `frontend/app.js` |
| Indicador de progreso ("caso 7 de 10") | ✅ Hecho | `frontend/app.js` |
| Guardar cada clic en `resultados.csv` al momento del clic | ✅ Hecho | `backend/server.py` → endpoint `POST /api/juicios` |
| Columnas del CSV: caso, id_correcto, posicion, id_resultado, score, juicio, quien, fecha | ✅ Hecho | `backend/server.py` |
| Retomar progreso si se cierra el navegador | ✅ Hecho | `frontend/app.js` → `cargarCasoActual()` |
| Pantalla final con Top 1, Top 5 y Utilidad | ✅ Hecho | `frontend/app.js` + `backend/server.py` → `GET /api/estadisticas` |
| Desglose por tipo de foto (persona, producto, captura, difícil) | ✅ Hecho | `backend/server.py` + `metricas.py` |
| Script standalone de métricas | ✅ Hecho | `metricas.py` |
| Botón "Volver a empezar" (re-evaluar) | ✅ Hecho | `frontend/app.js` + `POST /api/reset` |
| No tocar embeddings, products.csv ni el motor | ✅ Cumplido | Solo consumo de API vía `POST /search/image` |
| 10 casos de prueba con fotos externas | ✅ Hecho | `casos/caso-001.jpg` a `caso-010.jpg` + `casos.csv` |
| README con instrucciones para otra persona | ✅ Hecho | Este archivo |
| AI_LOG.md con cada prompt documentado | ✅ Hecho | `AI_LOG.md` |

---

## División de trabajo

### Samir Ochoa — Backend y pipeline de datos

- Definición del contrato de datos (`casos.csv` y `resultados.csv`).
- Implementación de `server.py`:
  - Proxy a la API del buscador (`GET /health`, `POST /search/image`).
  - Endpoints para listar casos, obtener caso con resultados, guardar juicios, exportar CSV, estadísticas, servir imágenes.
  - Guardado inmediato en disco (append al CSV al momento del clic).
  - Manejo de errores (API caída, imagen no encontrada, IDs desalineados).
  - Desglose de métricas por tipo de foto.
  - Endpoint `POST /api/reset` para re-evaluar.
- Implementación de `metricas.py` (script standalone).
- Obtención de los 10 casos de prueba (fotos reales de internet, no del catálogo).
- Creación de `casos.csv` con distribución: 3 persona, 3 producto, 2 captura, 2 difícil.
- Coordinación y redacción del README.

### Andrés Quispe — Frontend y experiencia de usuario

- Construcción de la pantalla de evaluación (`index.html`, `app.js`, `styles.css`):
  - Foto de consulta arriba, 5 resultados abajo en grid.
  - Tres botones por resultado con criterios visibles.
  - Botón "Siguiente" dinámico (se habilita solo al evaluar todos los resultados del caso).
  - Indicador de progreso arriba a la derecha.
  - Pantalla de métricas al terminar (Top 1, Top 5, Utilidad + tabla por tipo).
  - Botón "Volver a empezar".
- Guardado inmediato de cada clic vía `POST /api/juicios`.
- Retomar progreso tras cerrar navegador (busca el primer caso sin evaluar).
- Prevención de juicios duplicados (misma posición no se envía dos veces).
- Diseño visual elegante con estilo consistente al proyecto RAG-V2.

---

## Estructura del evaluador

```
evaluador/
├── README.md              # Este informe de avance
├── AI_LOG.md              # Registro de cada prompt de IA utilizado
├── casos/
│   ├── caso-001.jpg       # Fotos reales de camisetas (NO son del catálogo)
│   ├── caso-002.jpg
│   ├── ...
│   ├── caso-010.jpg
│   └── casos.csv          # caso, id_correcto, tipo
├── backend/
│   └── server.py          # Backend FastAPI (proxy + juicios + estadísticas)
├── frontend/
│   ├── index.html         # Pantalla de evaluación
│   ├── app.js             # Lógica del frontend
│   └── styles.css         # Estilos
├── metricas.py            # Script standalone de métricas
└── resultados.csv         # Se crea automáticamente al evaluar
```

---

## Cómo funciona

### Flujo de ejecución

```
Terminal 1: API del buscador (puerto 8000)
         ↓
Terminal 2: Evaluador (puerto 8001)
         ↓
Navegador: http://127.0.0.1:8001
         ↓
Caso 1 → Foto de consulta → API devuelve 5 resultados → Usuario califica → Se guarda en CSV
         ↓
Caso 2 → ... → Caso 10 → Pantalla de métricas
```

### Cómo se guarda cada clic

Cuando el usuario aprieta un botón (Acierto / Sirve / No sirve), el frontend envía un `POST /api/juicios` al backend. El backend escribe una fila inmediatamente en `resultados.csv`:

```
caso, id_correcto, posicion, id_resultado, score, juicio, quien, fecha
caso-001,AIM-P001-001,1,AIM-P001-001,0.9234,Acierto,Andres y Samir,2026-09-15 14:30:00
```

Si el navegador se cierra, al reabrir se lee el CSV existente y se retoma en el primer caso que tenga juicios pendientes.

### Cómo se calculan las métricas

| Número | Fórmula |
|---|---|
| **Top 1** | `casos_con_acierto_en_posicion_1 / total_casos * 100` |
| **Top 5** | `casos_con_algun_acierto_en_5_posiciones / total_casos * 100` |
| **Utilidad** | `suma_de_resultados_utiles_entre_todos_los_casos / total_casos` |

Donde "resultado útil" = recibió "Acierto" o "Sirve".

Los tres números se dividen por tipo de foto (persona, producto, captura, difícil) para identificar dónde falla el buscador.

---

## La API del buscador (qué ya existía)

| Endpoint | Qué devuelve |
|---|---|
| `GET /health` | JSON con `products`, `embeddings`, `model` |
| `POST /search/image` | Top 5 con `id`, `nombre`, `imagen`, `url`, `score` |

El evaluador solo consume estos dos endpoints. No toca embeddings, products.csv, ni el motor de búsqueda.

---

## Los 10 casos de prueba

| Caso | ID correcto | Tipo |
|---|---|---|
| caso-001 | AIM-P001-001 | persona |
| caso-002 | AIM-P001-002 | persona |
| caso-003 | AIM-P001-003 | persona |
| caso-004 | AIM-P001-004 | producto |
| caso-005 | AIM-P001-005 | producto |
| caso-006 | AIM-P001-006 | producto |
| caso-007 | AIM-P001-007 | captura |
| caso-008 | AIM-P001-008 | captura |
| caso-009 | AIM-P001-009 | dificil |
| caso-010 | AIM-P001-010 | dificil |

Las imágenes son fotos reales de internet, NO son las imágenes del catálogo. La foto no puede ser la imagen del catálogo porque si la pregunta y la respuesta son la misma imagen, la medición no vale nada.

---

## Endpoints del backend

| Endpoint | Método | Qué hace |
|---|---|---|
| `/` | GET | Sirve el frontend |
| `/health` | GET | Proxy a la API principal |
| `/api/casos` | GET | Lista los 10 casos |
| `/api/casos/{n}` | GET | Caso N + resultados del buscador |
| `/api/juicios` | POST | Guarda un juicio (clic) |
| `/api/resultados` | GET | Exporta resultados.csv |
| `/api/resultados/csv` | GET | Descarga resultados.csv |
| `/api/estadisticas` | GET | Calcula Top 1, Top 5, Utilidad |
| `/api/imagen/{nombre}` | GET | Sirve imágenes del catálogo |
| `/api/caso-imagen/{nombre}` | GET | Sirve fotos de consulta de los casos |
| `/api/reset` | POST | Limpia resultados.csv para re-evaluar |

---

## Cómo levantar

```powershell
# Terminal 1 — API del buscador
cd C:\Users\SAMIR\RAG-V2
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# Terminal 2 — Evaluador
cd C:\Users\SAMIR\RAG-V2
python evaluador\backend\server.py

# Navegador
http://127.0.0.1:8001
```

---

## Reglas del proyecto

- **[Nunca]** No tocar el buscador ni el índice. Solo consumir la API.
- **[Nunca]** No inventar casos con imágenes del catálogo.
- **[Con IA]** Usar IA todo lo que se quiera, anotar cada prompt en `AI_LOG.md`. Ambos integrantes deben poder explicar cada parte del código.
- **[Si se traban]** Más de 40 minutos atascados: escribir al coordinador.

---

## Próximos pasos

Si la herramienta funciona el lunes: entran los 180 casos de los diseñadores y sale el primer número honesto del proyecto.

- Si el número sale sobre 70%: el motor sirve. Siguiente paso: meterle los diseños propios de Sublitex.
- Si sale bajo 50%: el motor no está listo. Siguiente paso: arreglarlo con la ventaja de que ya tenemos una forma de saber si lo estamos mejorando.

Esta herramienta no se tira nunca. Es el instrumento de medida del proyecto.
