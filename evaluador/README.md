# Evaluador del Buscador — Ficha 03-A

Herramienta para calificar los resultados del buscador visual. Una persona ve una foto de consulta, los 5 resultados del buscador, y aprieta botones. Al final sale un numero.

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
│   └── server.py          # Backend FastAPI (proxy + juicios + estadisticas)
├── frontend/
│   ├── index.html         # Pantalla de evaluacion
│   ├── app.js             # Logica del frontend
│   └── styles.css         # Estilos
├── metricas.py            # Script standalone de metricas
└── resultados.csv         # Se crea automaticamente al evaluar
```

## Requisitos

1. La **API del buscador** debe estar corriendo en `http://127.0.0.1:8000`:
   ```powershell
   cd C:\Users\SAMIR\RAG-V2
   python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```

2. Dependencias del evaluador (ya estan en requirements.txt del proyecto):
   ```
   fastapi
   uvicorn
   requests
   python-multipart
   ```

## Como levantar el evaluador

```powershell
cd C:\Users\SAMIR\RAG-V2

# Opcion 1: directo
python evaluador\backend\server.py

# Opcion 2: con uvicorn
python -m uvicorn evaluador.backend.server:app --host 0.0.0.0 --port 8001

# Opcion 3: con variable de entorno para la API
$env:API_BASE_URL="http://127.0.0.1:8000"
python evaluador\backend\server.py
```

El evaluador corre en `http://127.0.0.1:8001`.

**IMPORTANTE**: No usar `0.0.0.0` en el navegador. Usar siempre `127.0.0.1` o `localhost`.

## Como evaluar

1. Abrir `http://127.0.0.1:8001` en el navegador.
2. Escribir el nombre de quien evalua en el campo "Evalua:" (arriba a la derecha).
3. Se muestra el caso 1 de 10: la foto de consulta arriba, los resultados abajo.
4. Para cada resultado, apretar uno de tres botones:
   - **Acierto**: es el mismo diseno, aunque cambie color, ano, escudo o sponsor.
   - **Sirve**: no es el mismo, pero se lo mostrarias al cliente y lo aceptarias.
   - **No sirve**: es otro diseno.
5. Apretar "Siguiente" para pasar al siguiente caso.
6. El avance se muestra arriba a la derecha: "Caso 7 de 10".
7. Si se cierra el navegador, al reabrir se retoma donde quedo.
8. Al terminar todos los casos, sale la pantalla de metricas con Top 1, Top 5 y Utilidad.

## Donde queda el CSV

Los juicios se guardan en `evaluador/resultados.csv` con columnas:

```
caso, id_correcto, posicion, id_resultado, score, juicio, quien, fecha
```

Se guarda **al momento del clic**, no al final. Si el navegador se cierra a la mitad, lo evaluado hasta ahi sigue estando.

## Las tres metricas

| Numero | Como se calcula |
|--------|----------------|
| **Top 1** | De todos los casos, en que porcentaje el resultado de la posicion 1 recibio "Acierto". |
| **Top 5** | De todos los casos, en que porcentaje hubo un "Acierto" en cualquiera de las posiciones. |
| **Utilidad** | Promedio de cuantos de los resultados recibieron "Acierto" o "Sirve". Va de 0 a 5. |

Los tres numeros tambien se dividen por **tipo de foto** (persona, producto, captura, dificil). Esa division es la que dice donde falla el buscador.

### Ver metricas

```powershell
# Opcion 1: desde el backend (API)
try { (Invoke-WebRequest -Uri "http://127.0.0.1:8001/api/estadisticas" -UseBasicParsing).Content } catch { "Error" }

# Opcion 2: script standalone
python evaluador\metricas.py

# Opcion 3: con ruta custom
python evaluador\metricas.py --csv evaluador\resultados.csv
```

## Endpoints del backend

| Endpoint | Metodo | Que hace |
|----------|--------|----------|
| `/` | GET | Sirve el frontend (index.html, app.js, styles.css) |
| `/health` | GET | Proxy a la API principal |
| `/api/casos` | GET | Lista los 10 casos |
| `/api/casos/{n}` | GET | Caso N + resultados del buscador |
| `/api/juicios` | POST | Guarda un juicio (clic) |
| `/api/resultados` | GET | Exporta resultados.csv |
| `/api/resultados/csv` | GET | Descarga resultados.csv |
| `/api/estadisticas` | GET | Calcula Top 1, Top 5, Utilidad |
| `/api/imagen/{nombre}` | GET | Sirve imagenes del catalogo (busca multiples extensiones) |
| `/api/caso-imagen/{nombre}` | GET | Sirve fotos de consulta de los casos |
| `/api/reset` | POST | Limpia resultados.csv para re-evaluar |

## Reglas importantes

- **No tocar** el buscador, los embeddings, products.csv ni el indice.
- Las imagenes de casos **no pueden ser** las imagenes del catalogo.
- Cada clic se guarda inmediatamente en disco.
- Si la API del buscador no responde, el evaluador muestra error pero no se rompe.
- El navegador puede cachear archivos viejos. Si los cambios no se ven, hacer **Ctrl+F5**.

## Verificacion (como la revisa el coordinador)

1. Seguir solo este README, sin preguntar nada.
2. Levantar la API y el evaluador.
3. Cargar los 10 casos y evaluarlos apretando botones.
4. Cerrar el navegador a la mitad y reabrir. Lo evaluado debe seguir.
5. Abrir `resultados.csv` y ver filas completas sin duplicados.
6. Ver los tres numeros, en total y por tipo de foto.
7. En la pantalla final, apretar "Volver a empezar" y verificar que se puede re-evaluar.
8. Explicar como se calcula el Top 5.
