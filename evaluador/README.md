# Evaluador del Buscador — Ficha 03-A

Herramienta para calificar los resultados del buscador visual. Una persona ve una foto de consulta, los 5 resultados del buscador, y aprieta botones. Al final sale un numero.

## Estructura

```
evaluador/
├── README.md              # Este archivo
├── AI_LOG.md              # Registro de prompts de IA
├── casos/
│   ├── caso-001.jpg       # 10 fotos externas de camisetas
│   ├── ...
│   ├── caso-010.jpg
│   └── casos.csv          # caso, id_correcto, tipo
├── backend/
│   └── server.py          # Backend FastAPI (proxy + juicios + estadisticas)
├── metricas.py            # Script standalone de metricas
└── resultados.csv         # Se crea automaticamente al evaluar
```

## Requisitos

1. La **API del buscador** debe estar corriendo en `http://127.0.0.1:8000`:
   ```bash
   cd /ruta/al/proyecto
   uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```

2. Dependencias del evaluador (ya estan en requirements.txt del proyecto):
   ```
   fastapi
   uvicorn
   requests
   python-multipart
   ```

## Como levantar el evaluador

```bash
cd /ruta/al/proyecto

# Opcion 1: directo
python evaluador/backend/server.py

# Opcion 2: con uvicorn
uvicorn evaluador.backend.server:app --host 0.0.0.0 --port 8001

# Opcion 3: con variable de entorno para la API
set API_BASE_URL=http://127.0.0.1:8000
python evaluador/backend/server.py
```

El evaluador corre en `http://127.0.0.1:8001`.

## Como evaluar

1. Abrir `http://127.0.0.1:8001` en el navegador.
2. Se muestra el caso 1 de 10: la foto de consulta arriba, los 5 resultados abajo.
3. Para cada resultado, apretar uno de tres botones:
   - **Acierto**: es el mismo diseño, aunque cambie color, ano, escudo o sponsor.
   - **Sirve**: no es el mismo, pero se lo mostrarias al cliente y lo aceptarias.
   - **No sirve**: es otro diseño.
4. Apretar "Siguiente" para pasar al siguiente caso.
5. El avance se muestra arriba a la derecha: "caso 7 de 10".
6. Si se cierra el navegador, al reabrir se retoma donde quedo.

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
| **Top 5** | De todos los casos, en que porcentaje hubo un "Acierto" en cualquiera de las 5 posiciones. |
| **Utilidad** | Promedio de cuantos de los 5 resultados recibieron "Acierto" o "Sirve". Va de 0 a 5. |

Los tres numeros tambien se dividen por **tipo de foto** (persona, producto, captura, dificil). Esa division es la que dice donde falla el buscador.

### Ver metricas

```bash
# Opcion 1: desde el backend (API)
curl http://127.0.0.1:8001/api/estadisticas

# Opcion 2: script standalone
python evaluador/metricas.py

# Opcion 3: con ruta custom
python evaluador/metricas.py --csv evaluador/resultados.csv
```

## Endpoints del backend

| Endpoint | Metodo | Que hace |
|----------|--------|----------|
| `/health` | GET | Proxy a la API principal |
| `/api/casos` | GET | Lista los 10 casos |
| `/api/casos/{n}` | GET | Caso N + resultados del buscador |
| `/api/juicios` | POST | Guarda un juicio (clic) |
| `/api/resultados` | GET | Exporta resultados.csv |
| `/api/resultados/csv` | GET | Descarga resultados.csv |
| `/api/estadisticas` | GET | Calcula Top 1, Top 5, Utilidad |
| `/api/reset` | POST | Limpia resultados.csv |

## Reglas importantes

- **No tocar** el buscador, los embeddings, products.csv ni el indice.
- Las imagenes de casos **no pueden ser** las imagenes del catalogo.
- Cada clic se guarda inmediatamente en disco.
- Si la API del buscador no responde, el evaluador muestra error pero no se rompe.

## Verificacion (como la revisa el coordinador)

1. Seguir solo este README, sin preguntar nada.
2. Cargar los 10 casos y evaluarlos apretando botones.
3. Cerrar el navegador a la mitad y reabrir. Lo evaluado debe seguir.
4. Abrir resultados.csv y ver filas completas.
5. Ver los tres numeros, en total y por tipo de foto.
6. Explicar como se calcula el Top 5.
