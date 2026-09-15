# Evaluador del Buscador — Ficha 03-A

**Sublitex · Ficha 03-A · Programación · Entrega: lunes**

Herramienta para que una persona califique los resultados del buscador visual y el sistema saque el número. La herramienta no busca nada: le pregunta al buscador (API) y muestra lo que responde.

## Qué se construyó

Una pantalla donde se ve una foto arriba, los cinco resultados del buscador abajo, y tres botones en cada resultado. Al final, un número.

| Componente | Qué hace | Archivo |
|---|---|---|
| **Backend FastAPI** | Proxy a la API del buscador, sirve casos, guarda juicios en disco, calcula estadísticas | `backend/server.py` |
| **Frontend HTML/JS/CSS** | Interfaz de evaluación con botones Acierto/Sirve/No sirve, pantalla de métricas | `frontend/index.html`, `app.js`, `styles.css` |
| **Script de métricas** | Calcula Top 1, Top 5 y Utilidad desde la terminal | `metricas.py` |
| **10 casos de prueba** | Fotos reales de camisetas con su ID correcto y tipo | `casos/` |

## Qué ya existe y no hay que construir

El buscador ya está hecho y funcionando. Tu herramienta solo consume la API.

| Campo | Valor | Por qué |
|---|---|---|
| API que ya existe | `POST /search/image` | Le mandas una imagen y te devuelve los 5 diseños más parecidos |
| Comprobar que está viva | `GET /health` | Si esto no responde, la API no está levantada |
| Lo que devuelve cada resultado | `id · nombre · imagen · url · score` | 5 resultados en un arreglo JSON, del más parecido al menos parecido |

## Estructura

```
evaluador/
├── README.md              # Este archivo
├── AI_LOG.md              # Registro de asistencia de IA
├── casos/
│   ├── caso-001.jpg       # 10 fotos externas de camisetas
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

## Requisitos previos

1. **Python 3.10+**
2. La **API del buscador** debe estar corriendo en `http://127.0.0.1:8000` antes de levantar el evaluador.

## Cómo levantar

### Paso 1: Levantar la API del buscador y comprobar que responde

```powershell
cd C:\Users\SAMIR\RAG-V2
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Abrir `http://127.0.0.1:8000/health` en el navegador. Tienes que ver un JSON que dice cuántos productos y cuántos embeddings tiene cargados. Si no son iguales entre sí, avisa al coordinador y no sigas: el índice está roto.

### Paso 2: Levantar el evaluador

```powershell
# Opción 1: directo
python evaluador\backend\server.py

# Opción 2: con uvicorn
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# Opción 3: con variable de entorno para la API
$env:API_BASE_URL="http://127.0.0.1:8000"
python evaluador\backend\server.py
```

El evaluador corre en `http://127.0.0.1:8001`.

**IMPORTANTE**: No usar `0.0.0.0` en el navegador. Usar siempre `127.0.0.1` o `localhost`.

## Los 10 casos de prueba

Los casos están en `evaluador/casos/`. Cada caso es una foto real de una camiseta sacada de internet (NO es la imagen del catálogo). El archivo `casos.csv` define:

```
caso,id_correcto,tipo
caso-001,AIM-P001-001,persona
caso-002,AIM-P001-002,persona
...
caso-010,AIM-P001-010,dificil
```

| Tipo | Cantidad | Qué significa |
|---|---|---|
| `persona` | 3 | Foto con persona usando la camiseta |
| `producto` | 3 | Foto tipo catálogo/producto |
| `captura` | 2 | Captura de pantalla o foto informal |
| `dificil` | 2 | Foto difícil (mala calidad, ángulo raro, etc.) |

## Cómo evaluar

1. Abrir `http://127.0.0.1:8001` en el navegador.
2. Escribir el nombre de quien evalúa en el campo "Evalúa:" (arriba a la derecha).
3. Se muestra el caso 1 de 10: la foto de consulta arriba, los resultados abajo.
4. Para cada resultado, apretar uno de tres botones:
   - **Acierto**: es el mismo diseño, aunque cambie color, año, escudo o sponsor.
   - **Sirve**: no es el mismo, pero se lo mostrarías al cliente y lo aceptarías.
   - **No sirve**: es otro diseño.
5. Apretar "Siguiente" para pasar al siguiente caso.
6. El avance se muestra arriba a la derecha: "Caso 7 de 10".
7. Si se cierra el navegador, al reabrir se retoma donde quedó.
8. Al terminar todos los casos, sale la pantalla de métricas con Top 1, Top 5 y Utilidad.

## Dónde queda el CSV

Los juicios se guardan en `evaluador/resultados.csv` con columnas:

```
caso, id_correcto, posicion, id_resultado, score, juicio, quien, fecha
```

Se guarda **al momento del clic**, no al final. Si el navegador se cierra a la mitad, lo evaluado hasta ahí sigue estando.

Ejemplo de fila:

```
caso-001,AIM-P001-001,1,AIM-P001-001,0.9234,Acierto,Andres y Samir,2026-09-15 14:30:00
```

## Las tres métricas

| Número | Cómo se calcula |
|---|---|
| **Top 1** | De todos los casos, en qué porcentaje el resultado de la posición 1 recibió "Acierto". |
| **Top 5** | De todos los casos, en qué porcentaje hubo un "Acierto" en cualquiera de las 5 posiciones. |
| **Utilidad** | Promedio de cuántos de los 5 resultados recibieron "Acierto" o "Sirve". Va de 0 a 5. |

Los tres números también se dividen por **tipo de foto** (persona, producto, captura, difícil). Esa división es la que dice dónde falla el buscador, y es la parte más útil de todo el trabajo.

### Ver métricas

```powershell
# Opción 1: desde el backend (API)
try { (Invoke-WebRequest -Uri "http://127.0.0.1:8001/api/estadisticas" -UseBasicParsing).Content } catch { "Error" }

# Opción 2: script standalone
python evaluador\metricas.py

# Opción 3: con ruta custom
python evaluador\metricas.py --csv evaluador\resultados.csv
```

## Endpoints del backend

| Endpoint | Método | Qué hace |
|---|---|---|
| `/` | GET | Sirve el frontend (index.html, app.js, styles.css) |
| `/health` | GET | Proxy a la API principal |
| `/api/casos` | GET | Lista los 10 casos |
| `/api/casos/{n}` | GET | Caso N + resultados del buscador |
| `/api/juicios` | POST | Guarda un juicio (clic) |
| `/api/resultados` | GET | Exporta resultados.csv |
| `/api/resultados/csv` | GET | Descarga resultados.csv |
| `/api/estadisticas` | GET | Calcula Top 1, Top 5, Utilidad |
| `/api/imagen/{nombre}` | GET | Sirve imágenes del catálogo (busca múltiples extensiones) |
| `/api/caso-imagen/{nombre}` | GET | Sirve fotos de consulta de los casos |
| `/api/reset` | POST | Limpia resultados.csv para re-evaluar |

## Reglas importantes

- **[Nunca]** No tocar el buscador ni el índice. Ni los embeddings, ni products.csv, ni el motor de búsqueda. La herramienta solo consume la API.
- **[Nunca]** No inventar casos con imágenes del propio catálogo. Es el error que ya arruinó la evaluación anterior.
- **[Con IA]** Se usó IA y se anotó cada prompt en `AI_LOG.md`.
- **[Si se traban]** Más de 40 minutos atascados en lo mismo: escribir al coordinador.

## Verificación (cómo la revisa el coordinador)

El coordinador va a hacer exactamente esto, delante de ustedes:

1. Seguir solo este README, sin preguntar nada.
2. Levantar la API y el evaluador.
3. Cargar los 10 casos y evaluarlos apretando botones.
4. Cerrar el navegador a la mitad y reabrir. Lo evaluado debe seguir.
5. Abrir `resultados.csv` y ver filas completas sin duplicados.
6. Ver los tres números, en total y por tipo de foto.
7. En la pantalla final, apretar "Volver a empezar" y verificar que se puede re-evaluar.
8. Preguntar a cada uno de los dos, por separado, cómo se calcula el Top 5. Si uno de los dos no lo sabe explicar, la pareja no aprueba aunque el código funcione.

## Solución de problemas

| Problema | Solución |
|---|---|
| El evaluador no carga resultados | Verificar que la API del buscador esté corriendo en puerto 8000 |
| Las imágenes no se ven | Hacer Ctrl+F5 para limpiar caché del navegador |
| "Error de conexión" en la pantalla | La API no está levantada. Levantar con `python -m uvicorn api.main:app --port 8000` |
| El CSV sale vacío | Verificar que los juicios se guardaron (reabrir el navegador y revisar) |
| No se puede re-evaluar | Usar el botón "Volver a empezar" en la pantalla final, o borrar `resultados.csv` manualmente |

## Informe diario

Al final de cada día, cuatro líneas al grupo:

1. Qué quedó funcionando hoy.
2. Qué no salió y por qué.
3. Cuánto tiempo se fue en lo que más costó.
4. Qué necesitan de otro para poder seguir mañana.

## Qué sigue después

Si la herramienta funciona el lunes: entran los 180 casos de los diseñadores y sale el primer número honesto del proyecto. Esa medición decide todo lo que viene después.

- Si el número sale sobre 70%: el motor sirve. Lo siguiente es meterle los diseños propios de Sublitex.
- Si sale bajo 50%: el motor no está listo, y lo siguiente es arreglarlo — con la ventaja de que ya tenemos una forma de saber si lo estamos mejorando o solo moviendo.

Esta herramienta no se tira nunca. Cada vez que alguien toque el buscador, se vuelve a pasar el examen con ella. Es el instrumento de medida del proyecto, y por eso importa más que sea confiable a que sea bonita.
