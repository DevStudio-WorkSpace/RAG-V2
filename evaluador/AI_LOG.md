# AI_LOG.md — Evaluador (Ficha 03-A)

Registro de prompts y decisiones de IA utilizadas en la construccion del Evaluador.

## Fecha: 2026-09-11

### Decisiones de arquitectura

- **Backend con FastAPI**: se eligio FastAPI por consistencia con la API principal del proyecto (tambien FastAPI). Permite CORS automatico, validacion de tipos, y documentacion automatica en /docs.
- **Proxy a la API**: el evaluador NO busca nada directamente. Llama a POST /search/image de la API principal para obtener los 5 resultados. Esto garantiza que siempre se mida el motor real.
- **Guardado inmediato**: cada clic se guarda con `csv.DictWriter` en modo append (`"a"`). Si el navegador se cierra o el servidor muere, lo que se guardo sigue en disco.
- **Metricas en dos sitios**: el endpoint `/api/estadisticas` calcula en tiempo real, y `metricas.py` es un script standalone que puede correrse sin el servidor.

### Estructura de carpetas

- `evaluador/casos/`: imagenes de prueba + casos.csv
- `evaluador/backend/`: server.py (FastAPI)
- `evaluador/metricas.py`: script de metricas standalone
- `evaluador/resultados.csv`: generado automaticamente al evaluar

### Prompts utilizados

1. **Prompt de analisis inicial**: "Dame lo que debemos hacer completar todo lo de grupo A al 100%" — se analizo la ficha 03-A y se genero un plan de trabajo dividido entre Samir Ochoa y Andres Quispe.

2. **Prompt de implementacion**: "Ya bueno avanza la parte de Samir Ochoa, que este al 100% su parte que no tenga ningun error que funcione al 100%" — se implemento el backend completo: server.py, metricas.py, casos.csv, README.md.

### Validaciones

- server.py usa `py_compile` para verificar que no tiene errores de sintaxis.
- metricas.py usa `py_compile` para verificar que no tiene errores de sintaxis.
- Los endpoints fueron disenados para no romperse si la API del buscador no esta disponible (devuelven error 503 con mensaje claro).
