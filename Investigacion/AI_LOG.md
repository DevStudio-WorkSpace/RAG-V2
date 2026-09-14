# AI_LOG - Fase de Investigación (Evaluador)

## Fecha: 2026-09-14 (Fase 3 y 4 - Herramienta de Evaluacion)

### Prompt - Investigacion de sesgos en metricas
**Proposito:** Responder al requerimiento de la Fase 4 investigando las formas en que la metrica de calidad se puede inflar sin mentir explicitamente (sesgos del evaluador, seleccion de casos, orden de presentacion).
**Resultado:** Se actualizo DECISIONES.md con el analisis de 3 sesgos (Cherry-picking, Fatiga y Position Bias) con su deteccion y prevencion. En base a esto se construyo Investigacion/evaluador.py, aplicando las medidas preventivas.

### Pruebas de Ejecución y Troubleshooting (Bugfixes)
Durante la prueba del simulacro, encontramos y resolvimos dos bugs críticos arquitectónicos de entorno y datos:

1. **Bug de Rutas Relativas (Path Resolution):**
   - **Problema:** Al ejecutar `streamlit run Investigacion/evaluador.py` desde la raíz del proyecto, Streamlit buscaba el archivo `casos_prueba.csv` en el directorio de ejecución actual (la raíz) y no donde residía el código, provocando un error de lectura.
   - **Solución:** Se reemplazaron las rutas de cadena cruda por rutas absolutas relativas al archivo empleando `os.path.join(os.path.dirname(__file__), "archivo.csv")`. Esto hace que el módulo evaluador sea portable e infalible respecto al `cwd` del usuario.

2. **Inconsistencia de Extensiones en la Base de Datos (`products.csv` vs filesystem):**
   - **Problema:** La API devolvía nombres de archivo como `AIM-P068-037.gif` basándose en el registro original de la base de datos `products.csv`. Sin embargo, durante el procesamiento del Hito 1, las imágenes fueron convertidas físicamente a formato `.jpg`. El evaluador buscaba la ruta exacta, y como `.gif` no existía físicamente en `images_normalized/`, la interfaz arrojaba "Imagen del resultado no encontrada".
   - **Solución:** Se implementó una lógica de `fallback` en `evaluador.py`. Si la ruta devuelta por la API falla (ej. `.gif`), el evaluador extrae el `base_name` y verifica si existe su equivalente en `.jpg` o `.png`, haciéndolo robusto frente a bases de datos con extensiones desactualizadas.
