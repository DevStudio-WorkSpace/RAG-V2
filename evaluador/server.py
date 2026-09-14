from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import csv
import os

from datetime import datetime

# ==========================================
# CREAR APLICACIÓN FASTAPI
# ==========================================

app = FastAPI(
    title="Servidor del Evaluador",
    version="1.0"
)

# ==========================================
# CONFIGURACIÓN CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# RUTA DEL ARCHIVO CSV
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ARCHIVO_CSV = os.path.join(
    BASE_DIR,
    "resultados.csv"
)

# ==========================================
# MODELO DE DATOS
# ==========================================

class Evaluacion(BaseModel):
    consulta: str
    resultado_id: str
    nombre: str
    posicion: int
    score: float
    evaluacion: str

# ==========================================
# CREAR CSV SI NO EXISTE
# ==========================================

def crear_csv_si_no_existe():

    if not os.path.exists(ARCHIVO_CSV):

        with open(
            ARCHIVO_CSV,
            "w",
            newline="",
            encoding="utf-8"
        ) as archivo:

            escritor = csv.writer(archivo)

            escritor.writerow([
                "fecha",
                "consulta",
                "resultado_id",
                "nombre",
                "posicion",
                "score",
                "evaluacion"
            ])

# ==========================================
# RUTA PRINCIPAL
# ==========================================

@app.get("/")
def inicio():

    return {
        "status": "ok",
        "mensaje": "Servidor del evaluador funcionando"
    }

# ==========================================
# GUARDAR EVALUACIÓN
# ==========================================

@app.post("/evaluar")
def guardar_evaluacion(evaluacion: Evaluacion):

    crear_csv_si_no_existe()

    with open(
        ARCHIVO_CSV,
        "a",
        newline="",
        encoding="utf-8"
    ) as archivo:

        escritor = csv.writer(archivo)

        escritor.writerow([
            datetime.now().isoformat(),
            evaluacion.consulta,
            evaluacion.resultado_id,
            evaluacion.nombre,
            evaluacion.posicion,
            evaluacion.score,
            evaluacion.evaluacion
        ])

    return {
        "ok": True,
        "mensaje": "Evaluación guardada correctamente",
        "resultado_id": evaluacion.resultado_id,
        "evaluacion": evaluacion.evaluacion
    }

# ==========================================
# OBTENER EVALUACIONES DE UNA CONSULTA
# ==========================================

@app.get("/evaluaciones/{consulta}")
def obtener_evaluaciones(consulta: str):

    crear_csv_si_no_existe()

    evaluaciones = []

    with open(
        ARCHIVO_CSV,
        "r",
        newline="",
        encoding="utf-8"
    ) as archivo:

        lector = csv.DictReader(archivo)

        for fila in lector:

            if fila["consulta"] == consulta:

                evaluaciones.append({
                    "fecha": fila["fecha"],
                    "consulta": fila["consulta"],
                    "resultado_id": fila["resultado_id"],
                    "nombre": fila["nombre"],
                    "posicion": int(fila["posicion"]),
                    "score": float(fila["score"]),
                    "evaluacion": fila["evaluacion"]
                })

    return {
        "consulta": consulta,
        "total": len(evaluaciones),
        "evaluaciones": evaluaciones
    }

# ==========================================
# EJECUTAR DIRECTAMENTE
# ==========================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "server:app",
        host="127.0.0.1",
        port=8001,
        reload=True
    )