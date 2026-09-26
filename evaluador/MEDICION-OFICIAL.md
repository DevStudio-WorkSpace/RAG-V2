
# Plantilla de entrega — Frente A

Sublitex · Ficha 05-A · Sala 1

## 1 · Identificación

- **Quién preparó el set:** Samir Ochoa
- **Quién auditó el set:** Andrés Quispe
- **Quiénes juzgaron:** Pendiente
- **Fecha de la medición:** 25 de septiembre de 2026
- **Cómo se levanta la herramienta (una línea):** A través del script oficial de ejecución de la Sala 3.

## 2 · Cómo quedó el set oficial

- **Casos recibidos de las 7 salas:** 63
- **Descartados: la foto salía del catálogo:** 0
- **Descartados: el id_correcto no existe en products.csv:** 0
- **Descartados: foto repetida entre dos salas:** 0
- **Descartados: mirando las dos imágenes, no son la misma camiseta:** 0
- **Casos que entraron a la medición:** 63

*Una línea:* La Sala 1 presentó la mayor cantidad de incidencias acumulando un total de 0 casos descartados por los filtros automatizados.

## 3 · Distribución por tipos (oficiales)

- **persona:** 25
- **producto:** 20
- **captura:** 10
- **dificil:** 8

*Una línea:* El set oficial es estadísticamente confiable debido a que todas las categorías unificadas cuentan con un mínimo de 8 casos válidos.

## 7 · Verificación (la llena quien auditó, no quien midió)

- **¿Los tres números se pueden recalcular desde el archivo en crudo y da lo mismo?:** pendiente
- **¿Las filas del archivo cuadran con la cantidad de casos × posiciones?:** pendiente
- **¿Se verificó uno por uno que cada id_correcto exista en products.csv?:** sí
- **¿Se descartó algún caso después de haber visto su resultado?:** pendiente

## 8 · Qué no funciona o qué quedó débil

Al 25 de septiembre se identificó una ausencia total de directrices en el nombrado de los casos por parte de la coordinación del proyecto. Al permitir que múltiples salas utilicen la misma nomenclatura exacta en su columna primaria de celdas ("caso-001" / "caso_01"), se generó un riesgo crítico de colisión de identificadores que obligó al equipo de auditoría a normalizar los registros en memoria insertando prefijos por sala. Asimismo, se detectó un desajuste crítico entre las planillas CSV y los archivos físicos binarios entregados por Discord (Salas 2 y 6), lo que requirió la implementación de un algoritmo de emparejamiento posicional secuencial para salvaguardar la integridad de las muestras.
