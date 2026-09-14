import csv
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "resultados.csv"

# -----------------------------------------------------
# COMPROBAR ARCHIVO
# -----------------------------------------------------

if not CSV_PATH.exists():
    print("ERROR: No se encontró resultados.csv")
    raise SystemExit

resultados = []

# -----------------------------------------------------
# LEER CSV
# -----------------------------------------------------

with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as archivo:
    lector = csv.DictReader(archivo)

    if lector.fieldnames is None:
        print("ERROR: El CSV no tiene encabezados.")
        raise SystemExit

    # Limpiar encabezados
    lector.fieldnames = [
        campo.strip().replace("*", "").replace("\\", "")
        for campo in lector.fieldnames
    ]

    print("Columnas detectadas:", lector.fieldnames)

    for fila in lector:
        # Limpiar claves
        fila = {
            clave.strip().replace("*", "").replace("\\", ""): valor
            for clave, valor in fila.items()
            if clave is not None
        }

        if not fila.get("consulta"):
            continue

        resultados.append({
            "fecha": fila.get("fecha", ""),
            "consulta": fila.get("consulta", ""),
            "resultado_id": fila.get("resultado_id", ""),
            "nombre": fila.get("nombre", ""),
            "posicion": int(fila.get("posicion", 0)),
            "score": float(fila.get("score", 0)),
            "evaluacion": fila.get("evaluacion", "").strip(),
        })

if not resultados:
    print("ERROR: No se encontraron evaluaciones.")
    raise SystemExit

# -----------------------------------------------------
# AGRUPAR POR CASO
# -----------------------------------------------------

casos = defaultdict(list)

for resultado in resultados:
    casos[resultado["consulta"]].append(resultado)

# -----------------------------------------------------
# CONTEO DE EVALUACIONES
# -----------------------------------------------------

conteo = Counter(
    resultado["evaluacion"]
    for resultado in resultados
)

aciertos = conteo.get("Acierto", 0)
sirve = conteo.get("Sirve", 0)
no_sirve = conteo.get("No sirve", 0)

total_casos = len(casos)
total_resultados = len(resultados)

# -----------------------------------------------------
# ANALIZAR ACIERTOS POR CASO
# -----------------------------------------------------

casos_con_acierto = 0
posiciones_aciertos = []
reciprocal_ranks = []

detalle_casos = []

for nombre_caso in sorted(casos.keys()):

    lista = casos[nombre_caso]

    encontrados = [
        resultado
        for resultado in lista
        if resultado["evaluacion"] == "Acierto"
    ]

    if encontrados:

        mejor = min(
            encontrados,
            key=lambda x: x["posicion"]
        )

        casos_con_acierto += 1

        posiciones_aciertos.append(
            mejor["posicion"]
        )

        reciprocal_ranks.append(
            1 / mejor["posicion"]
        )

        detalle_casos.append({
            "caso": nombre_caso,
            "estado": "ACIERTO",
            "posicion": mejor["posicion"],
            "producto": mejor["nombre"],
            "resultados": len(lista),
        })

    else:

        reciprocal_ranks.append(0)

        detalle_casos.append({
            "caso": nombre_caso,
            "estado": "SIN ACIERTO",
            "posicion": "-",
            "producto": "-",
            "resultados": len(lista),
        })

casos_sin_acierto = total_casos - casos_con_acierto

# -----------------------------------------------------
# MÉTRICAS
# -----------------------------------------------------

top5_accuracy = (
    casos_con_acierto / total_casos * 100
    if total_casos
    else 0
)

mrr = (
    sum(reciprocal_ranks) / total_casos
    if total_casos
    else 0
)

posicion_promedio = (
    sum(posiciones_aciertos)
    / len(posiciones_aciertos)
    if posiciones_aciertos
    else 0
)

score_promedio = (
    sum(resultado["score"] for resultado in resultados)
    / total_resultados
    if total_resultados
    else 0
)

# -----------------------------------------------------
# SCORES POR EVALUACIÓN
# -----------------------------------------------------

scores = defaultdict(list)

for resultado in resultados:
    scores[resultado["evaluacion"]].append(
        resultado["score"]
    )


def promedio(valores):
    if not valores:
        return 0

    return sum(valores) / len(valores)


# -----------------------------------------------------
# RESULTADOS
# -----------------------------------------------------

print()
print("=" * 60)
print("   ANÁLISIS DEL EVALUADOR DEL BUSCADOR VISUAL")
print("=" * 60)

print()
print("1. RESUMEN GENERAL")
print("-" * 60)

print(f"Casos evaluados:          {total_casos}")
print(f"Resultados evaluados:     {total_resultados}")
print(f"Aciertos:                 {aciertos}")
print(f"Sirve:                    {sirve}")
print(f"No sirve:                 {no_sirve}")

print()
print("2. RECUPERACIÓN")
print("-" * 60)

print(f"Casos con acierto:         {casos_con_acierto}")
print(f"Casos sin acierto:         {casos_sin_acierto}")
print(f"Top-5 Accuracy:            {top5_accuracy:.2f}%")
print(f"MRR:                       {mrr:.4f}")
print(f"Posición promedio acierto: {posicion_promedio:.2f}")

print()
print("3. SCORES")
print("-" * 60)

print(f"Score promedio general:    {score_promedio:.4f}")
print(f"Score promedio Acierto:    {promedio(scores['Acierto']):.4f}")
print(f"Score promedio Sirve:      {promedio(scores['Sirve']):.4f}")
print(f"Score promedio No sirve:   {promedio(scores['No sirve']):.4f}")

print()
print("4. DETALLE POR CASO")
print("-" * 60)

for detalle in detalle_casos:

    if detalle["estado"] == "ACIERTO":

        print(
            f"{detalle['caso']:<15} "
            f"{detalle['resultados']} resultados | "
            f"ACIERTO posición {detalle['posicion']} | "
            f"{detalle['producto']}"
        )

    else:

        print(
            f"{detalle['caso']:<15} "
            f"{detalle['resultados']} resultados | "
            f"SIN ACIERTO"
        )

print()
print("5. CONCLUSIÓN")
print("-" * 60)

print(
    f"El buscador recuperó el producto correcto en "
    f"{casos_con_acierto} de {total_casos} casos."
)

print(
    f"La precisión Top-5 obtenida fue de "
    f"{top5_accuracy:.2f}%."
)

if top5_accuracy >= 80:

    print(
        "El buscador presenta un rendimiento alto "
        "en las consultas evaluadas."
    )

elif top5_accuracy >= 50:

    print(
        "El buscador presenta un rendimiento intermedio. "
        "Recupera correctamente varios productos, pero "
        "todavía existen casos donde el producto esperado "
        "no aparece entre los primeros resultados."
    )

else:

    print(
        "El buscador presenta oportunidades de mejora "
        "en la recuperación visual."
    )

print()
print("=" * 60)
print("ANÁLISIS FINALIZADO")
print("=" * 60)