# EXPLICACION_TOP5.md

Guía clara y corta sobre Top 5 (Ficha 03-B). Pensada para que cualquier
integrante del equipo pueda explicarlo de memoria en la aceptación.

## Respuesta corta para la aceptación

> "Top 5 es el porcentaje de casos en los que al menos uno de los cinco
> resultados recibió Acierto. Sirve no cuenta como Acierto."

## 1. ¿Qué es Top 5?

Es una de las tres métricas que entrega el evaluador de la Ficha 03-B. Las
otras dos son Top 1 y Utilidad. Top 5 mira los cinco resultados que devuelve
el buscador para un caso y responde a una sola pregunta: ¿alguno de los cinco
es el diseño correcto (Acierto)?

## 2. Definición exacta (Ficha 03-B)

> "Top 5 = % de casos donde hubo un «Acierto» en cualquiera de las 5
> posiciones."

Fórmula:

```
Top 5 = (casos con al menos un Acierto entre las posiciones 1–5
         / total de casos evaluados) × 100
```

## 3. ¿Qué significa "Acierto"?

Lo fija la Ficha 03-B y el equipo no lo cambia:

> "Acierto: es el mismo diseño, aunque cambie el color, el año, el escudo o
> el sponsor."

Hay dos juicios más:

- **Sirve:** no es el mismo diseño, pero se lo mostrarías al cliente y lo
  aceptaría.
- **No sirve:** es otro diseño.

Para Top 5 solo importa Acierto.

## 4. ¿Qué pasa si hay un "Sirve" pero ningún "Acierto"?

Ese caso **no cuenta** para Top 5. Top 5 = 0 % para ese caso. Sirve puntúa
para Utilidad, pero no convierte un caso en Top 5.

## 5. ¿Qué pasa si hay varios "Aciertos"?

El caso cuenta **una sola vez** para Top 5. No importa si hay dos o cinco
Aciertos: el caso es "Top 5 = sí" y se suma 1 al numerador.

## 6. Diferencia entre Top 1 y Top 5

- **Top 1** mira SOLO la posición 1. Si ese resultado es Acierto, el caso
  suma; si no, no.
- **Top 5** mira las posiciones 1 a 5. Basta con que una de las cinco sea
  Acierto.

Top 5 ≥ Top 1 siempre (si Top 1 cuenta, Top 5 también).

## 7. ¿Cómo se calcula el porcentaje?

Se cuentan los casos cuyo Top 5 es "sí" (al menos un Acierto entre 1 y 5), se
divide por el total de casos evaluados y se multiplica por 100. Se redondea
para presentarlo.

Ejemplo numérico: si hay 10 casos evaluados y 9 tienen al menos un Acierto
entre las posiciones 1–5, Top 5 = 9/10 × 100 = 90 %.

## 8. Tres ejemplos concretos

### Ejemplo A — Caso Top 5 = SÍ, Top 1 = SÍ

| Pos | Resultado | Juicio |
|-----|-----------|--------|
| 1   | mismo diseño (otro año) | Acierto |
| 2   | otro | No sirve |
| 3   | otro | No sirve |
| 4   | otro | No sirve |
| 5   | otro | No sirve |

Top 1: SÍ (posición 1 es Acierto). Top 5: SÍ.

### Ejemplo B — Caso Top 5 = SÍ, Top 1 = NO

| Pos | Resultado | Juicio |
|-----|-----------|--------|
| 1   | otro diseño | No sirve |
| 2   | mismo diseño (cambia color) | Acierto |
| 3   | otro | No sirve |
| 4   | otro | No sirve |
| 5   | otro | No sirve |

Top 1: NO (la posición 1 no es Acierto). Top 5: SÍ (hay un Acierto en
posición 2). Aunque la posición 1 haya fallado, el caso recupera un Acierto
más abajo.

### Ejemplo C — Caso Top 5 = NO, Top 1 = NO

| Pos | Resultado | Juicio |
|-----|-----------|--------|
| 1   | otro | No sirve |
| 2   | otro | Sirve |
| 3   | otro | No sirve |
| 4   | otro | No sirve |
| 5   | otro | Sirve |

Top 1: NO. Top 5: NO (no hay ningún Acierto). Sirve no convierte el caso en
Top 5. Los dos "Sirve" puntúan para Utilidad (2/5 en este caso).

## 9. Ejemplo explícito: posición 1 No sirve, una posición 2–5 Acierto

| Pos | Juicio |
|-----|--------|
| 1   | No sirve |
| 2   | Acierto |
| 3   | No sirve |
| 4   | No sirve |
| 5   | No sirve |

- Top 1: **NO** cuenta (la posición 1 no es Acierto).
- Top 5: **SÍ** cuenta (hay un Acierto en posición 2).
- Utilidad: 1/5 (un Acierto, ningún Sirve adicional).

## 10. Ejemplo explícito: ningún Acierto, varios Sirve

| Pos | Juicio |
|-----|--------|
| 1   | No sirve |
| 2   | Sirve |
| 3   | Sirve |
| 4   | No sirve |
| 5   | Sirve |

- Top 1: NO.
- Top 5: **NO** (ningún Acierto).
- Utilidad: 3/5 (tres Sirve).

Aunque el buscador haya devuelto resultados "aceptables" para el cliente, no
son el diseño correcto, así que Top 5 = 0 % para ese caso.

## 11. ¿Por qué "Sirve" NO cuenta para Top 5?

Porque la Ficha 03-B define Top 5 mirando únicamente los "Aciertos". Sirve
tiene su propio papel: puntúa en la métrica Utilidad, pero no es lo mismo que
haber acertado con el diseño. Si Sirve contara para Top 5, se mezclarían dos
juicios distintos (diseño correcto vs. resultado presentable al cliente) y la
métrica dejaría de medir lo que tiene que medir.

## 12. ¿Cómo se calcula Top 5 para varios casos?

Pasos:

1. Se recorre cada caso evaluado (cada `caso_id` con juicios en
   `data/juicios.csv`).
2. Para cada caso se mira si en sus 5 juicios (`posicion` 1 a 5) hay al
   menos uno con valor `acierto`.
3. Se cuentan los casos en los que la respuesta a (2) es "sí".
4. Se divide por el total de casos evaluados y se multiplica por 100.

Ejemplo con 10 casos y 9 con al menos un Acierto: Top 5 = 9/10 × 100 = 90 %.

## 13. No confundir Top 5 con Utilidad

| Métrica | Qué cuenta | Rango |
|---------|------------|-------|
| Top 5 | Si hay al menos un Acierto en posiciones 1–5 | 0 – 100 % |
| Utilidad | Cuántos de los 5 resultados son Acierto o Sirve | 0 – 5 |

Un caso puede tener Utilidad alta (muchos Sirve) y aun así Top 5 = 0 % (ningún
Acierto). Y al revés: un caso con un solo Acierto en posición 5 ya tiene
Top 5 = sí, aunque su Utilidad sea solo 1/5.
