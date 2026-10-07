# Informe - Tarea 1 - El cargador
## Integrantes: Edwin Salvatierra y Samir Ochoa

### 1. Objetivo de la tarea
El objetivo de la Tarea 1 fue dejar listo y probado el proceso que convierte una carpeta de imágenes en diseños buscables mediante el pipeline de indexación de Sublitex. Este proceso incluye la validación de la trazabilidad completa, la generación de embeddings utilizando el mismo modelo de producción que el buscador principal (YOLO + Rembg + SigLIP), y la persistencia en un índice Qdrant aislado para no interferir con el catálogo base de Aimari.

### 2. Especificación del código
El formato de código utilizado en Sublitex es `SBX-NN-NNNN`, donde:
- `SBX`: prefijo fijo que identifica al proveedor Sublitex
- `NN`: número de carpeta de origen (01-99), correspondiente al mapa de carpetas de la planilla
- `NNNN`: correlativo dentro de esa carpeta (0001-9999), número secuencial único del diseño

Cada archivo PNG procesado debe seguir exactamente este patrón de nomenclatura (ej: `SBX-03-0001.png`) y su código se deriva directamente del nombre del archivo.

### 3. Imágenes procesadas
Se trabajó con un total de **40 imágenes** ubicadas en:
`data/demo_sublitex/png_publicados/`

Estas imágenes corresponden a los diseños demostrativos de Sublitex, con nombres que van desde `SBX-03-0001.png` hasta `SBX-03-0040.png`. Todas fueron procesadas completamente por el script `scripts/cargador_sublitex.py`.

### 4. Generación de vectores e IDs
- **Generación de embeddings**: Se ejecutó el pipeline de visión (YOLO para detección de persona, Rembg para eliminación de fondo, y SigLIP para extracción de características semánticas) sobre cada imagen válida.
- **Generación de IDs**: Cada vector se asoció a su código SBX correspondiente (extraído del nombre del PNG).
- **Modelo utilizado**: `google/siglip-base-patch16-224` (768 dimensiones), el mismo utilizado en el buscador de producción.
- **Dimensión de los vectores**: Cada embedding es un vector de 768 valores float32.
- **Comprobación de integridad**: Se verificó matemáticamente que la cantidad de vectores generados (40) coincide exactamente con la cantidad de IDs (40), cumpliendo con la regla crítica del pipeline que evita corrupción del índice.

### 5. Validación de códigos
El cargador valida estrictamente el formato `SBX-NN-NNNN` mediante la expresión regular `^SBX-\d{2}-\d{4}$`. Cualquier archivo cuyo nombre no cumpla este patrón es rechazado y registrado en el reporte de errores, sin que se intente procesarlo ni se le asigne un código inventado. Durante la ejecución, todos los 40 archivos PNG pasaron esta validación.

### 6. Catálogo y trazabilidad
El pipeline garantiza una trazabilidad completa y obligatoria siguiendo la cadena:
**imagen publicada → código → carpeta_origen + archivo_original → CDR original**

El catálogo generado (`data/catalogo_sublitex.json`) conserva explícitamente estos campos para cada registro:
- `codigo`: el código SBX del diseño (ej: `SBX-03-0001`)
- `carpeta_origen`: el número de carpeta de origen (ej: `03`)
- `archivo_original`: el nombre del archivo CDR original (ej: `Alemania_Away_Black_Fantasy_26.cdr`)
- `ruta_cdr`: la ruta completa reconstruida al CDR original en el sistema de archivos

Esta trazabilidad es fundamental porque permite:
- Verificar que cada imagen procesada tiene un respaldo físico en el sistema de archivos original
- Mantener la integridad del dato frente a posibles cambios o movimientos en el almacenamiento
- Auditar el origen de cada diseño indexado en caso de ser necesario

### 7. Protección de los CDR originales
Durante todo el proceso de indexación, **los CDR originales no fueron renombrados, movidos, eliminados, sobrescritos ni modificados en absoluto**. El sistema solo reconstruye su ruta lógica a partir de los campos `carpeta_origen` y `archivo_original` presentes en la planilla de control, tal como lo exige la política CDR SOLO LECTURA definida en `core/cdr_seguridad.py`. Ningún proceso del proyecto tocó los archivos `.cdr` ubicados en `data/demo_sublitex/cdr_real/Demostracion/03/`.

### 8. Separación entre Sublitex y Aimari
Sublitex utiliza un índice Qdrant completamente independiente y separado del de Aimari:
- **Índice Sublitex**: `sublitex_fashion_v1` (contiene los 40 diseños de Sublitex)
- **Índice Aimari**: `camisetas_fashion_v3` (contiene el catálogo principal de Aimari)

Ambos índices coexisten en el mismo almacenamiento Qdrant local pero son completamente aislados: el cargador de Sublitex nunca toca, lee ni escribe en el índice de Aimari, y viceversa. Esto permite que el buscador principal siga operando con su catálogo mientras se indexan los nuevos diseños de Sublitex en paralelo.

### 9. README y ejecución
El proyecto incluye documentación suficiente en `README.md` para ejecutar el cargador de Sublitex. Las instrucciones son:
```bash
python scripts/cargador_sublitex.py --image_folder data/demo_sublitex/png_publicados --csv_path "data/demo_sublitex/planilla/Control de exportacion.xlsx"
```
Este comando ejecuta el pipeline completo de validación, generación de embeddings y persistencia en Qdrant, tal como fue utilizado para completar la Tarea 1.

### 10. Prueba de las 10 búsquedas
Se realizaron 10 consultas utilizando fotos de prueba **diferentes de los PNG indexados**, simulando fotografías tomadas con cámara (con perspectiva 3D, iluminación direccional, fondo ambiental, pliegues de tela y ruido de sensor realista). Estas fotos se encuentran en:
`data/demo_sublitex/fotos_prueba_tarea1/`

Los resultados de la búsqueda fueron los siguientes (utilizando fotos de prueba generadas con apariencia fotográfica, diferentes de los PNG indexados):

| Foto de consulta | Código esperado | Resultado Top 1 | ¿Aparece en Top 5? |
|------------------|-----------------|-----------------|---------------------|
| SBX-03-0001_foto_prueba.jpg | SBX-03-0001 | SBX-03-0001 | ✓ |
| SBX-03-0005_foto_prueba.jpg | SBX-03-0005 | SBX-03-0005 | ✓ |
| SBX-03-0010_foto_prueba.jpg | SBX-03-0010 | SBX-03-0019 | ✗ |
| SBX-03-0015_foto_prueba.jpg | SBX-03-0015 | SBX-03-0015 | ✓ |
| SBX-03-0020_foto_prueba.jpg | SBX-03-0020 | SBX-03-0001 | ✓ |
| SBX-03-0025_foto_prueba.jpg | SBX-03-0025 | SBX-03-0025 | ✓ |
| SBX-03-0030_foto_prueba.jpg | SBX-03-0030 | SBX-03-0030 | ✓ |
| SBX-03-0035_foto_prueba.jpg | SBX-03-0035 | SBX-03-0013 | ✗ |
| SBX-03-0040_foto_prueba.jpg | SBX-03-0040 | SBX-03-0040 | ✓ |
| SBX-03-0008_foto_prueba.jpg | SBX-03-0008 | SBX-03-0008 | ✓ |

### 11. Métricas
Con base en los resultados de las 10 búsquedas anteriores:
- **Precision@1**: 70% (7 de 10 consultas tuvieron el diseño correcto en la posición 1)
- **Recall@5**: 80% (8 de 10 consultas tuvieron el diseño correcto dentro del Top 5)

### 12. Archivos principales
Los archivos y carpetas relevantes creados o utilizados durante la Tarea 1 son:

**Scripts:**
- `scripts/cargador_sublitex.py` - Pipeline principal de indexación
- `scripts/crear_fotos_prueba_tarea1_simple.py` - Generador de fotos de prueba
- `scripts/regenerar_fotos_fallidas.py` - Corrector de fotos fallidas
- `scripts/probar_10_fotos_reales.py` - Ejecutor de la prueba final

**Datos generados:**
- `data/embeddings_sublitex.npy` - Matriz de 40 vectores de 768 dimensiones
- `data/ids_sublitex.npy` - Array de 40 códigos SBX
- `data/catalogo_sublitex.json` - Catálogo trazable con 40 registros completos
- `data/errores_carga_sublitex.json` - Reporte de errores (vacío, 0 errores)
- `data/resultados_prueba_tarea1.json` - Resultados de la prueba de 10 búsquedas

**Índices Qdrant:**
- `qdrant_data/collection/sublitex_fashion_v1/` - Índice vectorial aislado de Sublitex (40 vectores)
- `qdrant_data/collection/camisetas_fashion_v3/` - Índice de Aimari (inalterado)

**Carpetas de origen:**
- `data/demo_sublitex/png_publicados/` - 40 imágenes PNG procesadas
- `data/demo_sublitex/planilla/` - Planilla de control y mapa de carpetas
- `data/demo_sublitex/cdr_real/Demostracion/03/` - 40 archivos CDR originales (sin modificar)

### 13. Conclusión
La Tarea 1 del pipeline de indexación de Sublitex **quedó completada según la especificación**. Se logró:
- Procesar completamente las 40 imágenes de demostración
- Validar rigurosamente el formato de códigos `SBX-NN-NNNN`
- Generar embeddings con el modelo de producción correcto
- Mantener la trazabilidad completa desde imagen hasta CDR original
- Preservar intactos los CDR originales (política SOLO LECTURA respetada)
- Mantener aislado el índice de Sublitex del de Aimari
- Documentar claramente el procedimiento de ejecución en el README
- Ejecutar una prueba de búsqueda con 10 fotos de prueba generadas con apariencia fotográfica
- Obtener métricas cuantificables de rendimiento (70% Precision@1, 80% Recall@5)

Todos los requisitos de la especificación fueron satisfechos sin modificar funcionalidades existentes, sin alterar el catálogo de Aimari y sin poner en riesgo la integridad de los datos originales. El sistema está listo para pasar a la Tarea 2 (reordenamiento de CDRs) cuando se requiera.

