# Plantilla de entrega — Frente A
Sublitex · Ficha 05-A · Sala 1

## 1 · Identificación
- **Quién preparó el set:** Samir Ochoa
- **Quién auditó el set:** Andrés Quispe
- **Quiénes juzgaron:** Pendiente (Asignados por el coordinador)
- **Fecha de la medición:** 23 de septiembre de 2026
- **Cómo se levanta la herramienta (una línea):** A través del script oficial de ejecución de la Sala 3.

## 2 · Cómo quedó el set oficial
- **Casos recibidos de las 7 salas:** Pendiente (Salas 4, 5 y 6 no entregaron archivo .csv)
- **Descartados: la foto salía del catálogo:** Pendiente
- **Descartados: el id_correcto no existe en products.csv:** Pendiente (Archivo maestro no provisto)
- **Descartados: foto repetida entre dos salas:** Pendiente
- **Descartados: mirando las dos imágenes, no son la misma camiseta:** Pendiente
- **Casos que entraron a la medición:** Pendiente

*Una línea:* Auditoría paralizada temporalmente. Las salas 4, 5 y 6 no adjuntaron sus planillas de datos, y la Sala 3 no ha compartido el archivo maestro products.csv.

## 7 · Verificación (la llena quien auditó, no quien midió)
- **¿Los tres números se pueden recalcular desde el archivo en crudo y da lo mismo?:** pendiente
- **¿Las filas del archivo cuadran con la cantidad de casos × posiciones?:** pendiente
- **¿Se verificó uno por uno que cada id_correcto exista en products.csv?:** No (Archivo maestro ausente en el repositorio)
- **¿Se descartó algún caso después de haber visto su resultado?:** pendiente

## 8 · Qué no funciona o qué quedó débil
Al iniciar el proceso de auditoría el 23 de septiembre, se detectó que el flujo de datos está roto en el origen. Las salas 5 y 6 subieron imágenes sin su respectivo registro indexado, la Sala 4 no presenta archivos, y no contamos con el archivo maestro `products.csv` para ejecutar el script de control de IDs. No se puede emitir un set limpio oficial hasta que los equipos regularicen sus entregas en el repositorio de GitHub.
