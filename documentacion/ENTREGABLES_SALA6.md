# 04. Qué se entrega el lunes (Sala 6)

- **Los tres números sobre el set original (el propio):**
  - Top 1 (Precision@1): 30.0%
  - Top 5 (Utilidad): 96.0%
  - Calidad (NDCG@5): 95.3%

- **Los tres números sobre el set nuevo (recibido de Sala 5):**
  - Top 1 (Precision@1): 60.0%
  - Top 5 (Utilidad): 68.0%
  - Calidad (NDCG@5): 75.7%

- **Una línea corta:** 
La utilidad general (Top 5) bajó drásticamente con el set nuevo porque nuestro set original era muy similar al catálogo ("examen fácil"), mientras que el set de la Sala 5 introdujo fondos ruidosos y posturas complejas que rompieron la detección del modelo, generando casos de fallo total (0 aciertos).

---

# 05. Informe Diario (Sala 6)

1. **Qué quedó funcionando hoy:** Quedó corriendo la evaluación de punta a punta de los dos sets. Además, integramos exitosamente el frontend de Next.js de la Sala 5 y actualizamos nuestro evaluador manual para soportar distintos "modos" de búsqueda.
2. **Qué no salió y por qué:** Algunos casos específicos del set ajeno (`C_05` y `C_07`) devolvieron 0 aciertos absolutos. Esto no salió porque asumimos que el modelo de CLIP extrae ruido del fondo o posturas raras de los modelos, arruinando el embedding.
3. **Qué número cambió al usar el set ajeno:** La exactitud pura (Top 1) sorprendentemente subió (del 30 al 60%), pero la Utilidad General en el Top 5 se desplomó (cayó del 96% al 68%).
4. **Qué necesitan de otro para seguir mañana:** Necesitamos confirmar con el resto si el motor de Reranking (Hito 2) o la mejora del Bounding Box logran rescatar estos casos extremos donde la similitud visual directa falla por el ruido del fondo.
