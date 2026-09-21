# Informe Final de Evaluación: Comparativa de Rendimiento

Este informe consolida los resultados de dos rondas de evaluación manual del motor de búsqueda visual (RAG-V2) sobre dos conjuntos de datos distintos. Ambos se evaluaron bajo el modo `original` (Hito 1, sin reranking adicional).

## 1. Métricas Consolidadas

| Métrica | Ronda 1 (Imágenes de Catálogo) | Ronda 2 (Nuevas Imágenes C_01 a C_10) | Variación |
| :--- | :--- | :--- | :--- |
| **Precision@1 (Acierto Exacto Top 1)** | 30.0% | **60.0%** | **+30.0%** |
| **Precision@5 (% de útiles en Top 5)** | **96.0%** | 68.0% | **-28.0%** |
| **NDCG@5 (Calidad del Ranking)** | **95.3%** | 75.7% | **-19.6%** |

## 2. Análisis del Comportamiento

### Ronda 1: Alta Utilidad, Baja Exactitud en Top 1
Las imágenes de la Ronda 1 eran altamente similares a las del catálogo. El modelo exhibió un comportamiento de **"recuperación generalizada"**:
- Le costó poner el diseño exacto en la posición número 1 (solo 30%), probablemente porque el catálogo tiene muchas camisetas similares (distintos años o ligeras variaciones) que el modelo de CLIP puntúa con valores casi idénticos.
- Sin embargo, **el 96% de los resultados devueltos servían**. El motor fue brillante encontrando opciones útiles y válidas para el usuario, logrando un ranking casi perfecto (NDCG 95.3%).

### Ronda 2: Efecto de "Todo o Nada" (Alta Exactitud, Menor Utilidad)
Al probar con imágenes completamente nuevas y ajenas al catálogo:
- Cuando el modelo reconoció la prenda, fue contundente y la posicionó primera de inmediato, **duplicando el Precision@1 al 60%**. 
- Sin embargo, la métrica de utilidad general cayó al 68%. Esto se explica por una **fuerte polarización**: o el modelo acierta perfecto (ej. C_04, C_09, C_10), o falla de manera catastrófica sin devolver nada útil (ej. C_05 y C_07).

## 3. Conclusiones y Próximos Pasos

El motor base basado puramente en embeddings de CLIP (Hito 1) funciona extremadamente bien para encontrar similitud semántica general (Ronda 1), pero sufre ante factores externos en fotos nuevas (Ronda 2).

Para solucionar la polarización de la Ronda 2 (los casos que fallaron completamente):
- **Es imperativo el uso del Reranking (Hito 2)**: Al evaluar en modo `auto` o `procesada`, el sistema aplicará un filtro por colores dominantes, escudos y estructura. Esto evitará que una imagen con fondo ruidoso o pose extraña traiga resultados que "no sirven".
- **Revisar Bounding Boxes**: Para las fotos nuevas que fallaron, se recomienda inspeccionar la visualización del recorte automático para asegurar que el modelo no esté generando el embedding a partir de ruido visual.
