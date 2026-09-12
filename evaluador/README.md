# Evaluador del Buscador (Grupo A)

Herramienta web para calificar los resultados del buscador visual: sube la
foto de cada caso, la API devuelve un Top 5 y una persona marca cada resultado
como **Acierto**, **Sirve** o **No sirve**. Cada clic se guarda al instante.

---

## 1 · Cómo levantar

Necesitas dos terminales.

**1) La API (obligatoria, el buscador):**

```bash
python -m uvicorn api.main:app --port 8000
```

**2) La interfaz de evaluación:**

```bash
cd frontend-next
npm install        # solo la primera vez
npm run dev        # abre http://localhost:3000/evaluacion
```

El frontend también corre en modo producción con `npm run build && npm start`.

> La página busca en la API en `http://localhost:8000`. Si la cambiaste de
> puerto, edita `API_URL` en `frontend-next/app/evaluacion/page.tsx`.

---

## 2 · Cómo cargar los casos

1. Pon las fotos de consulta (reales, de internet, **nunca del catálogo**) en
   `evaluador/casos/` con nombres `caso-001.jpg` … `caso-010.jpg`.
   - Si todavía no existe `evaluador/casos/`, la herramienta usa las imágenes
     de prueba de `data/Search-10/`.
2. Completa `evaluador/casos.csv` con las columnas
   `caso,id_correcto,tipo`:

   | columna | qué es |
   |---|---|
   | `caso` | nombre del archivo sin extensión: `caso-001` |
   | `id_correcto` | id del diseño correcto del catálogo (`AIM-P###-NNN`), si se sabe |
   | `tipo` | `persona`, `producto`, `captura` o `dificil` |

3. Escribe el nombre del/la evaluador/a en la barra superior, evalúa los casos
   y pulsa **Siguiente →** para avanzar.

> Los casos terminados se guardan en `evaluador/completados.json` para que no
> vuelvan a aparecer, aunque cierres el navegador.

---

## 3 · Dónde queda el CSV

Cada clic guarda una fila al instante en **`evaluador/resultados.csv`** con:

`caso, id_correcto, posicion, id_resultado, score, juicio, quien, fecha`

- `posicion` · 1-5 (lugar del resultado en el Top 5).
- `id_resultado` · id del producto devuelto por la API.
- `juicio` · `acierto`, `sirve` o `no_sirve`.
- `quien` · nombre del evaluador.

La **persistencia es real**: cierra el navegador, apaga la API o recarga la
página; lo calificado sigue en el CSV.

---

## 4 · Qué significan los números

Calcula las métricas con:

```bash
python evaluador/calcular.py
```

Te imprime (y guarda en `evaluador/metricas.txt`) los **3 números, en total y
por tipo de foto** (`persona`, `producto`, `captura`, `dificil`):

- **Top 1 (%)** — porcentaje de casos donde el resultado de la **posición 1**
  fue marcado **Acierto**. Mide qué tan seguido el mejor resultado es el correcto.
- **Top 5 (%)** — porcentaje de casos donde **al menos uno** de los 5
  resultados fue marcado **Acierto**. Mide si el diseño correcto aparece en el
  top (aunque no sea el primero).
- **Utilidad (0-5)** — promedio por caso de cuántos resultados fueron **Acierto**
  o **Sirve**. Mide qué tan lleno de resultados aceptables está el Top 5
  (0 = nada útil, 5 = los cinco sirven).

**Cómo se calcula el Top 5 (explicación de la revisión):** por cada caso se
mira si algún resultado del Top 5 tiene juicio `acierto`; Top 5 = casos con
al menos un acierto ÷ casos evaluados × 100.