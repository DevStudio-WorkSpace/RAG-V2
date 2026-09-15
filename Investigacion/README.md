# Herramienta de Evaluación (Ficha 03-C)

Esta carpeta contiene la herramienta aislada para evaluar de forma masiva y sin sesgos los resultados del buscador.

## Fases del Proyecto

Cumpliendo con lo establecido en la **Ficha 03-C**, el trabajo se divide en:

- **Fase 1 (Entender), Fase 2 (Decidir) y Fase 4 (Buscar errores):** Todo el razonamiento, análisis de métricas fallidas, y las decisiones de diseño sobre la herramienta están documentadas detalladamente en el archivo [`DECISIONES.md`](DECISIONES.md).
- **Fase 3 (Construir):** Es esta herramienta (`evaluador.py`) y sus reglas de evaluación rígidas.
- **Registro de IA:** Todos los prompts utilizados están en [`AI_LOG.md`](AI_LOG.md).

## Archivos

- `evaluador.py`: La aplicación interactiva en Streamlit.
- `casos_prueba.csv`: Los casos de prueba iniciales cargados automáticamente.
- `resultados_evaluacion.csv`: Archivo generado automáticamente donde se van guardando los votos de la evaluación en tiempo real (persistencia continua).

## Formato de Entrada (Decisión D3)

Para que los diseñadores puedan evaluar los 180 casos de forma ágil, la herramienta levanta automáticamente el lote desde un archivo CSV (`casos_prueba.csv`). El formato debe ser estrictamente este:

```csv
ruta_imagen,id_correcto
data/consultas/prueba1.jpg,AIM-P022-060
```
- **`ruta_imagen`**: Ruta relativa a la imagen de consulta.
- **`id_correcto`**: El ID oficial de la camiseta en el catálogo.

## Instrucciones para levantar la herramienta

Para levantar la herramienta "sin preguntar nada" (como pide la Entrega 2), seguí estos dos pasos:

1. **Asegurate de que la API principal del buscador está corriendo.** (Si no lo está, levántala desde la raíz del proyecto):
   ```bash
   uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```

2. **Levantá la interfaz del evaluador:**
   Abrí otra terminal, entrá a esta carpeta y ejecutá:
   ```bash
   cd Investigacion
   streamlit run evaluador.py
   ```

## Cómo evaluar

La interfaz mostrará la imagen de consulta y 1 resultado a la vez. 
Para votar más rápido, usá los atajos de teclado numérico:
- Presioná `1` para **Acierto** (3 pts): Es el mismo diseño (aunque cambie color/escudo/sponsor).
- Presioná `2` para **Sirve** (1 pts): No es el mismo, pero el cliente lo aceptaría.
- Presioná `3` para **No sirve** (0 pts): Es otro diseño distinto.

La aplicación guardará cada voto en `resultados_evaluacion.csv`. Si cerrás el navegador, al volver a abrirlo continuará desde el último caso evaluado sin perder datos. Al terminar, mostrará el resumen de métricas (Precision@1, Precision@5, NDCG@5).

## Modificaciones

Modificaciones y actualizaciones realizadas por: Paolo
