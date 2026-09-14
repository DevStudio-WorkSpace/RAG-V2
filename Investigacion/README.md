# Herramienta de Evaluación (Fase 3)

Esta carpeta contiene la herramienta aislada para evaluar de forma masiva y sin sesgos los resultados del buscador. 

## Archivos

- `evaluador.py`: La aplicación interactiva en Streamlit.
- `casos_prueba.csv`: Los 10 casos de prueba iniciales. Su formato debe ser estricto:
  - **`ruta_imagen`**: Ruta relativa a la imagen de consulta.
  - **`id_correcto`**: El ID oficial de la camiseta en el catálogo (ej. `AIM-P022-060`).
- `resultados_evaluacion.csv`: Archivo generado automáticamente donde se van guardando los votos (persistencia continua).

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
- Presioná `1` para **Acierto** (3 pts)
- Presioná `2` para **Sirve** (1 pts)
- Presioná `3` para **No sirve** (0 pts)

La aplicación guardará cada voto en `resultados_evaluacion.csv`. Si cerrás el navegador, al volver a abrirlo continuará desde el último caso evaluado. Al terminar, mostrará el resumen de métricas (Precision@1, Precision@5, NDCG@5).
