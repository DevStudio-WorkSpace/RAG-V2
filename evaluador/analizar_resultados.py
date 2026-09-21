import pandas as pd
import os

# ==========================================
# RUTA DEL CSV
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_CSV = os.path.join(BASE_DIR, "resultados.csv")


# ==========================================
# VERIFICAR ARCHIVO
# ==========================================

if not os.path.exists(ARCHIVO_CSV):
    print("❌ No se encontró resultados.csv")
    exit()


# ==========================================
# LEER RESULTADOS
# ==========================================

df = pd.read_csv(ARCHIVO_CSV)

if df.empty:
    print("❌ El archivo resultados.csv está vacío.")
    exit()


# ==========================================
# DATOS GENERALES
# ==========================================

total_casos = df["consulta"].nunique()
total_resultados = len(df)

aciertos = len(df[df["evaluacion"] == "Acierto"])
sirve = len(df[df["evaluacion"] == "Sirve"])
no_sirve = len(df[df["evaluacion"] == "No sirve"])


# ==========================================
# PORCENTAJES
# ==========================================

porcentaje_aciertos = (
    aciertos / total_resultados
) * 100

porcentaje_sirve = (
    sirve / total_resultados
) * 100

porcentaje_no_sirve = (
    no_sirve / total_resultados
) * 100


# ==========================================
# TOP-5 ACCURACY
#
# Un caso cuenta como correcto si al menos
# un resultado fue marcado como "Acierto".
# ==========================================

casos_con_acierto = (
    df[df["evaluacion"] == "Acierto"]["consulta"]
    .nunique()
)

top5_accuracy = (
    casos_con_acierto / total_casos
) * 100


# ==========================================
# POSICIONES DE LOS ACIERTOS
# ==========================================

resultados_acertados = df[
    df["evaluacion"] == "Acierto"
][
    [
        "consulta",
        "resultado_id",
        "nombre",
        "posicion",
        "score",
    ]
].copy()

resultados_acertados["similitud"] = (
    resultados_acertados["score"] * 100
).round(2)


# ==========================================
# MOSTRAR REPORTE
# ==========================================

print()
print("=" * 55)
print("       REPORTE DE EVALUACIÓN DEL BUSCADOR")
print("=" * 55)

print()
print("RESUMEN GENERAL")
print("-" * 55)

print(f"Casos evaluados:       {total_casos}")
print(f"Resultados evaluados:  {total_resultados}")

print()
print("CLASIFICACIÓN HUMANA")
print("-" * 55)

print(
    f"Acierto:   {aciertos:>2} "
    f"({porcentaje_aciertos:.2f}%)"
)

print(
    f"Sirve:     {sirve:>2} "
    f"({porcentaje_sirve:.2f}%)"
)

print(
    f"No sirve:  {no_sirve:>2} "
    f"({porcentaje_no_sirve:.2f}%)"
)

print()
print("PRECISIÓN DEL BUSCADOR")
print("-" * 55)

print(
    f"Casos con al menos un acierto: "
    f"{casos_con_acierto}/{total_casos}"
)

print(
    f"Top-5 Accuracy: {top5_accuracy:.2f}%"
)

print()
print("POSICIÓN DE LOS ACIERTOS")
print("-" * 55)

if resultados_acertados.empty:

    print("No se encontraron aciertos.")

else:

    for _, fila in resultados_acertados.iterrows():

        print(
            f"{fila['consulta']} -> "
            f"posición {int(fila['posicion'])} | "
            f"{fila['nombre']} | "
            f"{fila['similitud']:.2f}%"
        )


# ==========================================
# RESULTADO POR CADA CASO
# ==========================================

print()
print("RESULTADO POR CASO")
print("-" * 55)

for consulta, grupo in df.groupby("consulta"):

    tiene_acierto = (
        grupo["evaluacion"] == "Acierto"
    ).any()

    cantidad = len(grupo)

    if tiene_acierto:
        estado = "ACIERTO EN TOP-5"
    else:
        estado = "SIN ACIERTO"

    print(
        f"{consulta}: "
        f"{estado} "
        f"({cantidad} resultados)"
    )


print()
print("=" * 55)
print("              FIN DEL REPORTE")
print("=" * 55)
print()