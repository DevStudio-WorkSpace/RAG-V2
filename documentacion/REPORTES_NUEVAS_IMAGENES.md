# Informe de Evaluación 2: Pruebas con Nuevas Imágenes (C_01 a C_10)

En esta segunda iteración de evaluación manual, se sometieron al motor de búsqueda visual 10 nuevas consultas de prueba (del archivo `C_01.jpg` al `C_10.jpg`).

## 1. Métricas Globales Obtenidas

| Métrica | Valor Obtenido | Interpretación |
| :--- | :--- | :--- |
| **Precision@1 (Exactitud)** | **60.0%** | En el 60% de los casos, el resultado en la primera posición (`Top 1`) fue clasificado como un **Acierto** exacto por el evaluador manual. |
| **Precision@5 (Utilidad)** | **68.0%** | Del total de los 50 resultados devueltos (5 por cada caso), el 68% fue considerado útil (ya sea como *Acierto* o como diseño alternativo que *Sirve*). |
| **NDCG@5 (Calidad del Ranking)** | **75.7%** | Indica qué tan bien están ordenados los resultados útiles. Un 75% es un puntaje sólido, lo que significa que los aciertos suelen estar efectivamente en los primeros lugares, y no relegados al final de la lista. |

## 2. Análisis por Casos de Rendimiento Extremo

### Casos Exitosos (Pleno de aciertos en primeras posiciones)
- **C_04.jpg**, **C_09.jpg**, **C_10.jpg**: Mostraron una capacidad de recuperación excelente. El motor no solo acertó el diseño exacto en la posición 1, sino que también encontró alternativas altamente útiles en las posiciones subsecuentes (muchos puntajes de `3`).
- **C_06.jpg**: Recuperación muy sólida con aciertos en las posiciones 1, 3, 4 y 5. 

### Casos de Bajo Rendimiento (Falsos Positivos o Sin Resultados Útiles)
- **C_05.jpg** y **C_07.jpg**: Ambos casos fallaron catastróficamente, obteniendo 0 aciertos y 0 resultados útiles en el Top 5 (`No sirve` en todas las posiciones). Esto puede deberse a:
  1. Que la camiseta consultada **no exista en el índice** (imposibilidad de encontrarla).
  2. Que la imagen tenga elementos externos que confundan al embedding (ej. un fondo muy ruidoso, postura del modelo compleja) y el recorte/preprocesamiento automático no esté logrando aislar la prenda correctamente.
- **C_08.jpg**: Solo el resultado en la Posición 1 fue considerado medianamente útil (`Sirve`), cayendo el resto a `No sirve`. 

## 3. Conclusiones y Siguientes Pasos

El motor demuestra **una sólida recuperación de base (60% de exactitud P@1)** en consultas nuevas que no estaban en el conjunto original, demostrando que los embeddings generalizan bastante bien para una gran parte de las imágenes. 

Sin embargo, hay un margen de mejora evidente (32% de los resultados en el Top 5 no sirven, concentrados fuertemente en casos específicos que fallan por completo). 

**Recomendaciones para el Hito 2 / Optimización:**
1. **Analizar los casos `C_05` y `C_07`**: Revisar en la nueva vista web (usando el modo `procesada`) qué es lo que está recortando el modelo. Si el bounding box falla, el CLIP extraerá características del fondo y no de la remera.
2. **Afinar Reranking**: Utilizar el nuevo frontend Next.js para correr estos mismos 10 casos en modo `auto` (con reranking por color, forma y escudos) para ver si los casos que fallaron mejoran sus resultados o son filtrados correctamente.
