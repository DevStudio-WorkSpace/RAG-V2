# -*- coding: utf-8 -*-
import csv

with open(r"C:\Users\SAMIR\RAG-V2\evaluador\resultados.csv", "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

casos = {}
for r in rows:
    c = r["caso"]
    if c not in casos:
        casos[c] = []
    casos[c].append(r)

total = len(casos)
top1_count = 0
top5_count = 0
suma_util = 0

for caso_id, juicios in casos.items():
    pos1 = [j for j in juicios if j["posicion"] == "1"]
    j1 = pos1[0]["juicio"] if pos1 else "?"
    hit_top1 = (pos1 and j1 == "Acierto")
    if hit_top1:
        top1_count += 1

    hay_acierto = any(
        j["juicio"] == "Acierto" and j["posicion"] in ("1","2","3","4","5")
        for j in juicios
    )
    if hay_acierto:
        top5_count += 1

    utiles = sum(
        1 for j in juicios
        if j["juicio"] in ("Acierto", "Sirve")
        and j["posicion"] in ("1","2","3","4","5")
    )
    suma_util += utiles
    print(f"  {caso_id}: pos1={j1} | utiles={utiles}/5")

util = round(suma_util / total, 2) if total else 0
print()
print(f"Total casos: {total}")
print(f"Top 1: {round(100*top1_count/total,1)}% ({top1_count}/{total})")
print(f"Top 5: {round(100*top5_count/total,1)}% ({top5_count}/{total})")
print(f"Utilidad: {util} / 5.00")
