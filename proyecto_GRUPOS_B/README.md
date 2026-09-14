# Evaluador Ficha 03-B

## Qué hace

Este evaluador permite medir la calidad del buscador visual RAG-V2 mediante juicios humanos.

El evaluador NO modifica RAG-V2. Solo consulta la API existente por HTTP y permite calificar los resultados.

## Requisitos

1. RAG-V2 debe estar corriendo en el puerto 8000.
2. Python 3.10+ con las dependencias instaladas.

## Cómo iniciar

### 1. Iniciar RAG-V2

Desde la raíz de RAG-V2:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Instalar dependencias del evaluador

```bash
cd proyecto_GRUPOS_B
pip install -r requirements.txt
```

### 3. Iniciar el evaluador

```bash
streamlit run app.py
```

El evaluador estará disponible en: http://localhost:8501

## Preparar los casos

### Dónde colocar las fotos

Las fotos externas de consulta deben colocarse en:

```
proyecto_GRUPOS_B/casos/fotos/
```

**IMPORTANTE:** Las fotos NO pueden proceder del catálogo (`data/images_normalized/`) ni de la web de Aimari. Deben ser fotografías externas.

### Formato de casos.csv

El archivo `casos/casos.csv` define los casos a evaluar:

```csv
caso_id,foto,tipo,id_correcto
caso_01,01.jpg,con_marco,AIM-P001-001
caso_02,02.jpg,sin_marco,AIM-P001-002
```

Columnas:
- `caso_id`: identificador único del caso
- `foto`: nombre del archivo en `casos/fotos/`
- `tipo`: tipo de foto de consulta. Las categorías actualmente en uso son `con_marco` y `sin_marco`
- `id_correcto`: ID del diseño correcto en el catálogo (NO se muestra durante la evaluación)

### Tipos de foto utilizados actualmente

El equipo decidió trabajar con dos tipos de foto:

- `con_marco`: la camiseta aparece dentro de un contexto/marco visible alrededor de ella.
- `sin_marco`: la camiseta aparece sobre fondo limpio, sin marco ni contexto.

La Ficha 03-B exige mostrar las métricas separadas por tipo de foto, pero no impone nombres concretos. Por tanto, `con_marco` y `sin_marco` son una decisión del equipo y se pueden cambiar en el futuro ampliando `casos.csv` con los nuevos tipos; el evaluador los lee dinámicamente.

### Cómo se cargan los casos (pensado para los 180 casos futuros)

1. Colocar la foto de la camiseta en `casos/fotos/` con el nombre que se quiera usar.
2. Añadir una fila en `casos/casos.csv` con `caso_id`, `foto`, `tipo` e `id_correcto`.
3. El evaluador detecta el caso automáticamente al recargar; no hace falta reiniciar nada más que la página de Streamlit.

Este formato (CSV + carpeta de fotos) es la decisión del equipo para que los 180 casos que vendrán después puedan entrar sin modificar el programa.

## Significado de los juicios

- **ACIERTO:** Es el mismo diseño, aunque cambie el color, el año, el escudo o el sponsor.
- **SIRVE:** No es el mismo diseño, pero se lo mostrarías al cliente y lo aceptaría.
- **NO SIRVE:** Es otro diseño.

## Definición de las métricas

### Top 1

Porcentaje de casos donde el resultado en posición 1 recibió «ACIERTO».

```
Top 1 = casos con ACIERTO en posición 1 / total de casos evaluados
```

### Top 5

Porcentaje de casos donde hubo un «ACIERTO» en cualquiera de las 5 posiciones.

```
Top 5 = casos con al menos un ACIERTO en posiciones 1-5 / total de casos evaluados
```

### Utilidad

Promedio de cuántos de los 5 resultados recibieron «ACIERTO» o «SIRVE».

```
Utilidad = suma(cantidad de ACIERTO o SIRVE por caso) / número de casos evaluados
```

Se muestra como `X.XX / 5`.

## Dónde se guardan los juicios

Cada juicio se guarda inmediatamente en:

```
proyecto_GRUPOS_B/data/juicios.jsonl
```

Formato (una línea JSON por juicio):

```json
{"caso_id": "caso_01", "tipo": "con_marco", "posicion": 1, "id_resultado": "AIM-P001-001", "juicio": "acierto", "score": 0.9608, "timestamp": "2026-09-13T10:30:00Z"}
```

## Persistencia

Los juicios se guardan en disco. Al cerrar y reabrir Streamlit, el evaluador reconstruye el progreso desde `juicios.jsonl`.

Si un resultado ya fue evaluado, el juicio se actualiza en lugar de duplicarse.

## Comprobar las métricas

Las métricas se calculan automáticamente desde `juicios.jsonl` después de cada juicio y al recargar la página.

Para verificar manualmente, abre `juicios.jsonl` con cualquier editor de texto.

## Estructura de archivos

```
proyecto_GRUPOS_B/
├── app.py
├── README.md
├── AI_LOG.md
├── requirements.txt
├── casos/
│   ├── casos.csv
│   └── fotos/
│       ├── 01.jpg
│       ├── 02.jpg
│       └── ... 10.jpg
└── data/
    └── juicios.jsonl
```

## Reglas importantes

1. **NO modificar RAG-V2** mientras se evalúa. Si el buscador cambia, la medición no significa nada.
2. **Las fotos de consulta NO pueden proceder del catálogo ni de Aimari.** Una sola foto del catálogo invalida la entrega completa.
3. El `id_correcto` en `casos.csv` es solo para verificar resultados, NO se muestra durante la evaluación.
4. El juicio siempre lo hace una persona, no un programa.

## Solución de problemas

### "No se pudo conectar a RAG-V2"

Asegúrate de que RAG-V2 esté corriendo:
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### "Falta la foto del caso"

Verifica que la foto exista en `casos/fotos/` y que el nombre coincida exactamente con `casos.csv`.

### "Imagen no encontrada"

Si una imagen del catálogo no existe localmente, se muestra un error en la interfaz. El evaluador no descarga imágenes automáticamente.
