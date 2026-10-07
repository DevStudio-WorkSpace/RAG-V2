# SECCION 00 — AUDITORIA DEL CONTRATO DE DATOS (Sublitex)

- Fecha de la auditoria: 2026-10-07
- Repositorio auditado: `RAG-V2-sala5`
- Alcance: SOLO LECTURA. No se modifico, renombro, movio ni borro ningun dato original.
  `git status` al inicio y al final de la auditoria: 0 cambios.
- Entregables de esta fase:
  - `docs/SECCION_00_AUDITORIA.md` (este informe, evidencia estatica)
  - `scripts/auditoria_seccion00.py` (auditoria automatizada, repetible y de solo lectura)
  - `docs/SECCION_00_REPORTE.md` (salida generada por el script sobre el estado actual)

---

## 1. Regla del codigo

Formato definitivo (ratificado tras investigar todas las fuentes del repo):

```
SBX-XXXXX    ->   ^SBX-\d{5}$
                 XXXXX = exactamente 5 digitos (consecutivo GLOBAL, 1..99999)
```

- Validos: `SBX-00001`, `SBX-00147`, `SBX-08340`, `SBX-11000`, `SBX-99999`.
- Invalidos: `SBX-0001`, `SBX-03-0147`, `SBX-000147`, `SBX_00001`,
  `SBX-00001-extra`, `XXX-00001`, `SBX-AB-XYZ`, `00001`, `01_0001`.

**Motivo de la ratificacion (resolucion de CRITICO-1):**
- La unica fuente oficial del cliente para esta tarea es la **Ficha 05-B**
  (Frente B, "Los disenos de Sublitex entran al buscador"), que define los ids
  del indice como **"Los códigos SBX-00001"** y describe los disenos internos
  como `001, 002, 003` (escala proyectada de ~11.000 unidades, que exige un
  consecutivo de 5 digitos).
- El formato `SBX-NN-NNNN` (carpeta-correlativo) solo aparece en codigo y
  documentacion generados por el proyecto (`cargador_sublitex.py`,
  `README.md`, tests), **ningun documento oficial lo respalda**.
- Consecuencia de diseño: el numero de carpeta **NO se codifica en el codigo**;
  vive en la columna `carpeta_origen` de la planilla y se resuelve con la hoja
  `Listas`.

## 2. Regla del archivo

```
SBX-XXXXX.png
```

La validacion se hace sobre el nombre base (`os.path.splitext`) con el regex de
arriba, mas la extension `.png` exacta y la firma binaria PNG
(`89 50 4E 47 0D 0A 1A 0A`). Lo implementa `scripts/auditoria_seccion00.py`;
el cargador (`cargador_sublitex.py`) valida el nombre base via
`core/sublitex.py::validar_codigo`.

## 3. Planilla encontrada

- Nombre esperado: **Control de exportacion**
- Ruta: **NO DISPONIBLE** — no existe en el repo, en el historico de git,
  ni en `Downloads`, `Documents`, `OneDrive`, `WPS Cloud`, `Mis documentos`,
  ni en los proyectos hermanos (`RAG-V2`, `RAG-V2-sala3`, `SALA-3`,
  `LAB-SALA-1`, `mi-bootcamp`).
- Formato: n/a (no hay `.xlsx`, `.xls` ni `.ods` en el repo ni en `git log --all`).
- Hoja principal: n/a. Hoja **Listas**: n/a.
- Unico vestigio: ayuda de CLI de `cargador_sublitex.py:132`
  (`--csv_path` "Control de exportacion") y `README.md:331`.

**No se inventan datos.** Mientras la planilla no exista, `codigo`,
`carpeta_origen` y `archivo_original` son irrecuperables.

## 4. Columnas encontradas

Esperadas (9): `codigo, carpeta_origen, archivo_original, tipo, deporte,
ocasion, estado, quien, fecha`.

Resultado: **no hay planilla, no hay columnas que comparar.**

Nota: la Ficha 05-B oficial menciona SOLO 4 columnas aportadas por diseno
(`tipo, deporte, ocasion, estado`), unidas por `codigo`. El esquema de 9
columnas (agrega `carpeta_origen, archivo_original, quien, fecha`) es una
extension NO documentada en la fuente oficial: validar contra la planilla real.

## 5. Mapa de carpetas (hoja Listas)

**NO DISPONIBLE.** No existe la hoja "Listas" ni ningun mapa
`numero -> carpeta real` en el repo ni en disco.

Con el formato ratificado `SBX-XXXXX` el numero de carpeta ya no se deriva del
codigo: se lee de la columna `carpeta_origen` de la planilla y se resuelve con
la hoja `Listas`. Mientras no exista esa hoja, `carpeta_origen` se conserva
literal de la planilla y la resolucion al CDR queda pendiente de datos reales
(sin inventar).

## 6. PNG encontrados

- Carpeta candidata `data/imagenes_normalized/`: EXISTE.
- Contenido: **44 archivos `.jpg`** (JPEG real, firma `FF D8 FF E0`) con nombres
  descriptivos (p. ej. `Argentina Kit Local 2026.jpg`).
- **PNG validos (`SBX-XXXXX.png`): 0. Invalidos: 44.**
- Duplicados exactos de nombre: 0. Sospechosos: `Costa Rica Away Kit 26 (1).jpg`
  (copia tipo "...(1)") y 2 con doble espacio (`Lineas Puntos Verde  Morado.jpg`,
  `Venezuela Home  Kit 26.jpg`).
- Origen: commit `0c359ce` "Subiendo las 44 imagenes del drive de Sublitex"
  (2026-10-06, Flavio Estrada). No los consume ningun script
  (grep `imagenes_normalized` -> 0 usos en codigo).
- PNG totales del repo: 12, todos ajenos a Sublitex (contact sheets,
  `evaluation/test_images`, montajes de consultas).
- `data/imagenes_normalized/` NO existe como carpeta en disco ni en `HEAD`.

## 7. Cruce PNG <-> planilla

| Metrica | Resultado |
| --- | --- |
| PNG valido + fila encontrada | 0 |
| PNG valido + fila inexistente | 0 (no hay PNG validos) |
| PNG invalidos | 44 |
| Fila de planilla sin PNG | n/a (sin planilla) |
| Codigo duplicado | n/a |
| carpeta_origen vacio | n/a |
| archivo_original vacio | n/a |

Cruce **inejecutable**: no existen los dos extremos de la cadena.

## 8. Problemas encontrados

### CRITICO

1. **~~Conflicto de formato del codigo~~ RESUELTO.** El `SBX-03-0147` del
   proyecto carece de respaldo oficial; la Ficha 05-B define `SBX-00001`
   (5 digitos, consecutivo global). Se adopto **`SBX-XXXXX` (`^SBX-\d{5}$`)**
   en todo el codigo: `core/sublitex.py`, `scripts/cargador_sublitex.py`,
   `scripts/auditoria_seccion00.py` y `tests/test_sublitex.py`. El numero de
   carpeta se resuelve por la columna `carpeta_origen` + hoja `Listas`.
2. **0 PNG de Sublitex** (se esperan ~40/44). Archivo: `data/imagenes_normalized/*.jpg`.
   Impacto: la cadena `imagen -> codigo` no puede iniciarse; la Tarea 1 no tiene insumo.
   Solucion: pedir la exportacion real del equipo con nomenclatura **`SBX-XXXXX.png`**
   (no renombrar nada).
3. **Planilla "Control de exportacion" inexistente** (y hoja Listas).
   Impacto: `carpeta_origen` + `archivo_original` -> CDR es irrecuperable.
   Solucion: solicitar el XLSX/CSV original. NO inventar.
4. **El commit HEAD `0c359ce` BORRO las 15.272 imagenes de Aimari**
   (`data/images_normalized/AIM-*.jpg`, status `D` en `git show 0c359ce`).
   Impacto: `data/images_normalized/` no existe en disco y es la carpeta unica
   del buscador (`api/search_engine_hito2.py:127`, `utils/helpers.py:10`,
   `scripts/precomputar_descriptores.py:45`, `scripts/consolidar.py:33`,
   `frontend/src/app/api/images/[filename]/route.ts:22`). Reranking, servido de
   imagenes y evaluaciones quedan rotos; viola la regla "no se toca lo de Aimari".
   Solucion: restaurar desde git (`git checkout 0c359ce^ -- data/images_normalized`),
   previa confirmacion. NO ejecutar sin orden.

### ALTO

5. **44 archivos sin el contrato de nombre/formato** (`.jpg` con nombres libres).
   Impacto: el cargador actual los rechazaria 100% (el formato vigente es
   `SBX-XXXXX.png`).
   Solucion: obtener PNG con nomenclatura oficial o escribir copias renombradas
   en OTRA carpeta (permitido por Ficha 05-B; los originales no se tocan).
6. **Cantidades disonantes: README dice "40 PNGs" (README.md:331), el commit dice
   "44 imagenes", los PNG reales son 0.** Solucion: contar la exportacion real.
7. **Columnas disonantes: 9 (espec) vs 4 (Ficha 05-B).** Solucion: validar contra
   la planilla real.

### MEDIO

8. `scripts/cargador_sublitex.py` ya implementa la Tarea 1 pero NUNCA se ejecuto
   (no hay `data/embeddings_sublitex.npy` ni `ids_sublitex.npy`; en Qdrant solo
   existe `camisetas_fashion_v3`). Y rompe la regla de la especificacion: si un
   PNG no tiene fila en el CSV usa `carpeta_origen="Desconocida"` y
   `archivo_original=<nombre del PNG>` (lineas 76-80) en lugar de reportarlo.
9. Nombres con doble espacio y sufijo `(1)` en 3 de los 44 JPG.

### BAJO

10. `README.md:331-343` describe la Tarea 1 como ya construida y menciona
    `control_exportacion.csv`, lo que sugiere que el archivo existe.
11. `data/imagenes_normalized/` es huerfana (ningun script la lee) y conviven
    dos carpetas con nombres casi identicos (`images_normalized` vs
    `imagenes_normalized`).

## 9. Cadena de trazabilidad

```
PNG -> codigo -> carpeta_origen + archivo_original -> CDR
 ❌       ❌                 ❌ (planilla inexistente)      ❌ (CDR sin ubicar)
```

**Hoy la cadena NO es trazable en ningun eslabon.**

## 10. Recomendacion para la Tarea 1

El futuro cargador debe consumir, en este orden y sin romper la cadena:

1. Carpeta de PNG `SBX-XXXXX.png`, validada con `^SBX-\d{5}$`;
   los invalidos se REPORTAN (no se corrigen ni se ignoran en silencio).
2. Planilla Control de exportacion como fuente unica de `carpeta_origen` y
   `archivo_original`, unida por `codigo`; cada PNG sin fila y cada fila sin
   PNG se lista en un archivo aparte (quitar el fallback `Desconocida`).
3. Hoja/CSV Listas como mapa `numero -> carpeta real` para llegar al CDR;
   mientras no exista, `carpeta_origen` se conserva LITERAL de la planilla.
4. Catalogo de salida (coleccion/npy NUEVA, p. ej. `sublitex_fashion_v1`) con
   `codigo + carpeta_origen + archivo_original`, mismo modelo del buscador y
   verificacion `len(vectores) == len(ids)`.

**Bloqueantes externos (dependen de datos reales, no de codigo):**
(a) PNG reales con nomenclatura `SBX-XXXXX.png`, (b) planilla real + hoja
Listas, (c) restaurar `data/images_normalized/` (Aimari) previa confirmacion.

---

## Anexo: uso del script de auditoria

```bash
# Estado actual (sin planilla ni lista: detecta y reporta NO DISPONIBLE)
python scripts/auditoria_seccion00.py

# Con insumos reales cuando existan
python scripts/auditoria_seccion00.py \
  --png_dir ruta/a/png_sublitex \
  --planilla "ruta/Control de exportacion.xlsx" \
  --salida docs/SECCION_00_REPORTE.md
```

El script es de SOLO LECTURA: nunca modifica PNG, planilla ni mapa. Su unico
archivo escrito es la salida del informe (`docs/SECCION_00_REPORTE.md` por
defecto). No genera embeddings ni toca el indice de Aimari.