# INFORME COMPARATIVO DE RESULTADOS DEL EVALUADOR VISUAL

## 1. Descripción

Se realizó una comparación entre dos archivos de resultados obtenidos mediante el sistema de búsqueda visual. La evaluación se realizó utilizando tres categorías:

* **Acierto:** el resultado corresponde correctamente a la imagen consultada.
* **Sirve:** el resultado tiene características útiles o similares.
* **No sirve:** el resultado no es relevante para la consulta.

Ambos archivos contienen evaluaciones de **10 casos de prueba**.

## 2. Comparación general

| Indicador                     | Resultados 1 | Resultados 2 |
| ----------------------------- | -----------: | -----------: |
| Casos evaluados               |           10 |           10 |
| Resultados registrados        |           42 |           48 |
| Aciertos                      |            5 |            0 |
| Sirve                         |           12 |           10 |
| No sirve                      |           25 |           38 |
| Casos con al menos un acierto |            5 |            0 |
| Promedio del score            |       0.5264 |       0.5067 |

## 3. Distribución de las evaluaciones

### Archivo de resultados 1

| Evaluación | Cantidad | Porcentaje |
| ---------- | -------: | ---------: |
| Acierto    |        5 |    11.90 % |
| Sirve      |       12 |    28.57 % |
| No sirve   |       25 |    59.52 % |
| **Total**  |   **42** |  **100 %** |

### Archivo de resultados 2

| Evaluación | Cantidad | Porcentaje |
| ---------- | -------: | ---------: |
| Acierto    |        0 |        0 % |
| Sirve      |       10 |    20.83 % |
| No sirve   |       38 |    79.17 % |
| **Total**  |   **48** |  **100 %** |

## 4. Resultados por caso

| Caso     | Resultados 1                   | Resultados 2        |
| -------- | ------------------------------ | ------------------- |
| Caso 001 | 2 Sirve, 3 No sirve            | 1 Sirve, 4 No sirve |
| Caso 002 | 1 Acierto, 1 Sirve, 3 No sirve | 1 Sirve, 4 No sirve |
| Caso 003 | 1 Sirve, 4 No sirve            | 2 Sirve, 3 No sirve |
| Caso 004 | 1 Acierto                      | 5 No sirve          |
| Caso 005 | 1 Acierto, 1 No sirve          | 1 Sirve, 4 No sirve |
| Caso 006 | 1 Acierto, 2 Sirve, 2 No sirve | 1 Sirve, 4 No sirve |
| Caso 007 | 3 Sirve, 2 No sirve            | 5 No sirve          |
| Caso 008 | 3 Sirve, 2 No sirve            | 2 Sirve, 3 No sirve |
| Caso 009 | 5 No sirve                     | 1 Sirve, 4 No sirve |
| Caso 010 | 1 Acierto, 3 No sirve          | 1 Sirve, 2 No sirve |

## 5. Posición de los aciertos

En el primer archivo se registraron cinco aciertos:

| Caso     | Producto identificado                | Posición |  Score |
| -------- | ------------------------------------ | -------: | -----: |
| Caso 002 | Jersey Millonarios Blue              |        3 | 0.4971 |
| Caso 004 | Liverpool Tercera Equipación 2026-27 |        1 | 0.5995 |
| Caso 005 | Newcastle United                     |        1 | 0.4351 |
| Caso 006 | Boca Juniors 2026-27 Third           |        4 | 0.4202 |
| Caso 010 | Costa De Marfil                      |        2 | 0.5217 |

En el segundo archivo no se registraron resultados clasificados como **Acierto**.

## 6. Promedio del score según evaluación

| Categoría | Resultados 1 |  Resultados 2 |
| --------- | -----------: | ------------: |
| Acierto   |       0.4947 | No registrado |
| Sirve     |       0.5365 |        0.5110 |
| No sirve  |       0.5279 |        0.5056 |

## 7. Cantidad de resultados por caso

En el primer archivo se registraron entre **1 y 5 resultados por consulta**. Los casos 004, 005 y 010 presentaron menos de cinco resultados.

En el segundo archivo se registraron cinco resultados en la mayoría de los casos. El caso 010 presentó tres resultados.

## 8. Diferencias observadas

* El primer archivo contiene **42 resultados**, mientras que el segundo contiene **48**.
* El primer archivo registra **5 aciertos** y el segundo no registra aciertos.
* La cantidad de resultados clasificados como **No sirve** aumentó de 25 a 38.
* La cantidad de resultados clasificados como **Sirve** disminuyó de 12 a 10.
* El promedio general del score pasó de **0.5264 a 0.5067**.
* En el primer archivo, los aciertos aparecieron entre las posiciones 1 y 4.
* En el segundo archivo, ningún resultado fue marcado como acierto.
