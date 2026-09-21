# Informe Ronda 2 — Sala 1

**Fecha:** 21 de septiembre de 2026
**Integrantes:** Andres y Samir
**Herramienta:** Evaluador visual (Ficha 03-A) + API FastAPI + buscador fusion (CLIP + OpenCLIP + SigLIP)

---

## 1. Los tres números — Set original (nuestros 10 casos)

| Métrica | Valor |
|---------|-------|
| Top 1 | 10.0% (1/10) |
| Top 5 | 10.0% (1/10) |
| Utilidad | 1.7 / 5.00 |

**Detalle por caso:**

| Caso | Tipo | Top 1 | Útiles (de 5) |
|------|------|-------|----------------|
| caso-001 | persona | No | 0 |
| caso-002 | persona | No | 2 |
| caso-003 | persona | No | 1 |
| caso-004 | producto | **Sí** | 1 |
| caso-005 | producto | No | 3 |
| caso-006 | producto | No | 1 |
| caso-007 | captura | No | 2 |
| caso-008 | captura | No | 1 |
| caso-009 | dificil | No | 2 |
| caso-010 | dificil | No | 4 |

---

## 2. Los tres números — Set de Sala 7 (14 casos ajenos)

| Métrica | Valor |
|---------|-------|
| Top 1 | 21.4% (3/14) |
| Top 5 | 21.4% (3/14) |
| Utilidad | 2.36 / 5.00 |

**Detalle por caso:**

| Caso | Top 1 | Útiles (de 5) |
|------|-------|----------------|
| BANRURAL | No | 1 |
| FRANCE | No | 5 |
| LA GUAIRA | No | 1 |
| LISIADOS | No | 1 |
| LOS INCREDIBLES | No | 1 |
| MBAPE tirado | No | 1 |
| MayasFC | No | 1 |
| SemenoSports | No | 3 |
| Sports | No | 3 |
| SportsPatron | **Sí** | 3 |
| YMAL tirado | **Sí** | 5 |
| cr7 tirado | **Sí** | 2 |
| hermanoSport | No | 2 |
| messi | No | 4 |

---

## 3. Comparación

| Métrica | Set original (10) | Set Sala 7 (14) | Cambio |
|---------|-------------------|------------------|--------|
| Top 1 | 10.0% | 21.4% | +11.4 pp |
| Top 5 | 10.0% | 21.4% | +11.4 pp |
| Utilidad | 1.70 | 2.36 | +0.66 |

**Los tres números subieron con el set ajeno.** La utilidad mejoró de 1.7 a 2.36, lo que significa que en promedio el buscador devolvió más resultados útiles por caso. El Top 1 también subió, pasando de 1 caso correcto a 3.

**Por qué creemos que pasó:** Los casos de Sala 7 son fotos de camisetas tiradas o planas (BANRURAL, FRANCE, cr7 tirado, etc.), que aunque son fotos reales, muestran la prenda de forma más visible que nuestras fotos originales (que incluían personas de costado, capturas de pantalla y mockups). El motor rinde mejor cuando la camiseta ocupa buena parte de la imagen.Tambien que la mayoria de imagen son los mockups.

---

## 4. Informe diario

### 4.1 Qué quedó funcionando hoy

- El evaluador (Ficha 03-A) funciona correctamente con los 14 casos de Sala 7: recibe fotos, llama a la API, muestra resultados y guarda cada juicio en disco.
- La API con motor fusion responde estable para las 14 consultas (lo cual esas era la cantidad de casos de la sala-7).
- Se completó el intercambio: enviamos nuestro set a Sala 2 y recibimos el de Sala 7.
- Se pudieron calcular las 3 métricas sobre ambos sets y comparar.

### 4.2 Qué no salió y por qué

- El `casos.csv` de Sala 7 venía con `id_correcto` vacío, lo que causaba que los juicios no se guardaran (FastAPI rechazaba el POST). Se resolvió poniendo el nombre del caso como placeholder.
- Solo pudimos obtener 3 "Acierto" de 14 casos. Las fotos de Sala 7 no son del catálogo, así que el motor no puede encontrar el diseño exacto — solo resultados visualmente parecidos.
- La utilidad promedio de 2.36 indica que, de los 5 resultados, en promedio menos de 3 son útiles para el usuario.

### 4.3 Qué número cambió al usar el set ajeno

- Top 1: subió de 10.0% a 21.4% (+11.4 puntos porcentuales).
- Top 5: subió de 10.0% a 21.4% (+11.4 puntos porcentuales).
- Utilidad: subió de 1.70 a 2.36 (+0.66 puntos).
- Todos los indicadores mejoraron con el set de Sala 7.

### 4.4 Qué necesitan de otro para seguir mañana

- Que Sala 7 complete la evaluación de sus 14 casos con su propia herramienta para tener comparación cruzada.
- Que nos envíen los `id_correcto` reales de sus fotos si los identifican, para poder medir Top 1 y Top 5 de forma exacta.

---

## 5. Archivos generados

| Archivo | Contenido |
|---------|-----------|
| `evaluador/casos/` | 14 imágenes de Sala 7 + casos.csv |
| `evaluador/resultados.csv` | 70 juicios nuestros (14 casos × 5 resultados) |
| `evaluador/resultados_set_original.csv` | 50 juicios de nuestro set original |
| `evaluador/casos_set_original.csv` | casos.csv de nuestro set original |
| `evaluador/casos_originales/` | 10 fotos de nuestro set original |
