# -*- coding: utf-8 -*-
"""
server.py — Backend del Evaluador (Ficha 03-A)
================================================
Servidor FastAPI que:
  1. Proxy a la API principal del buscador (POST /search/image, GET /health).
  2. Sirve los 10 casos de prueba desde casos/casos.csv.
  3. Guarda cada clic (juicio) en resultados.csv al momento del clic.
  4. Exporta resultados.csv completo y calcula estadisticas.
  5. Sirve archivos estaticos del frontend.

Puerto por defecto: 8001 (la API del buscador corre en 8000).

Uso:
    cd evaluador
    python backend/server.py
    # o desde la raiz del proyecto:
    # python evaluador/backend/server.py
"""

import csv
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# ── Configuracion ──────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent          # evaluador/
BACKEND_DIR = Path(__file__).resolve().parent               # evaluador/backend/
PROJECT_DIR = BASE_DIR.parent                              # raiz del proyecto
CASOS_DIR = BASE_DIR / "casos"
CASOS_CSV = CASOS_DIR / "casos.csv"
RESULTADOS_CSV = BASE_DIR / "resultados.csv"
FRONTEND_DIR = BASE_DIR  # frontend estatico en evaluador/ (Andres lo creara)

API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")
EVALUADOR_PORT = int(os.environ.get("EVALUADOR_PORT", "8001"))

RESULTADOS_COLUMNS = [
    "caso", "id_correcto", "posicion", "id_resultado", "score", "juicio", "quien", "fecha"
]


# ── App FastAPI ────────────────────────────────────────────────────────────
app = FastAPI(
    title="Evaluador del Buscador — Ficha 03-A",
    description="Herramienta para calificar los resultados del buscador visual.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Utilidades ─────────────────────────────────────────────────────────────

def _leer_casos() -> list[dict]:
    """Lee casos/casos.csv y devuelve una lista de dicts."""
    if not CASOS_CSV.exists():
        raise HTTPException(status_code=500, detail="No existe casos/casos.csv")
    with open(CASOS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def _imagen_caso_path(caso_nombre: str) -> Path:
    """Devuelve la ruta absoluta de la imagen de un caso."""
    # Buscar extensiones comunes
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        ruta = CASOS_DIR / f"{caso_nombre}{ext}"
        if ruta.exists():
            return ruta
    # Buscar sin extension si ya la tiene
    ruta = CASOS_DIR / caso_nombre
    if ruta.exists():
        return ruta
    return CASOS_DIR / f"{caso_nombre}.jpg"


def _guardar_juicio(juicio: dict):
    """Append de un juicio al archivo resultados.csv. Crear si no existe."""
    archivo_existe = RESULTADOS_CSV.exists() and RESULTADOS_CSV.stat().st_size > 0
    with open(RESULTADOS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RESULTADOS_COLUMNS)
        if not archivo_existe:
            writer.writeheader()
        writer.writerow(juicio)


def _leer_resultados() -> list[dict]:
    """Lee todo resultados.csv. Devuelve lista vacia si no existe."""
    if not RESULTADOS_CSV.exists():
        return []
    with open(RESULTADOS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def _calcular_estadisticas(resultados: list[dict]) -> dict:
    """
    Calcula Top 1, Top 5 y Utilidad a partir de los juicios guardados.

    Top 1:    % de casos donde el resultado en posicion 1 recibio "Acierto".
    Top 5:    % de casos donde hubo un "Acierto" en cualquiera de las 5 posiciones.
    Utilidad: promedio de cuantos de los 5 resultados fueron "Acierto" o "Sirve" (0-5).
    """
    if not resultados:
        return {
            "total_casos_evaluados": 0,
            "top1": 0.0,
            "top5": 0.0,
            "utilidad": 0.0,
            "por_tipo": {},
        }

    # Agrupar por caso
    casos_map: dict[str, list[dict]] = {}
    for r in resultados:
        caso_id = r.get("caso", "")
        if caso_id not in casos_map:
            casos_map[caso_id] = []
        casos_map[caso_id].append(r)

    total_casos = len(casos_map)
    casos_top1 = 0
    casos_top5 = 0
    suma_utilidad = 0.0

    # Por tipo
    tipo_stats: dict[str, dict] = {}

    # Cargar tipos desde casos.csv una sola vez
    tipos_map: dict[str, str] = {}
    try:
        casos_data = _leer_casos()
        for c in casos_data:
            tipos_map[c["caso"]] = c.get("tipo", "desconocido")
    except Exception:
        pass

    for caso_id, juicios in casos_map.items():
        tipo = tipos_map.get(caso_id, "desconocido")

        # Top 1: posicion 1 con "Acierto"
        pos1 = [j for j in juicios if j.get("posicion") == "1"]
        if pos1 and pos1[0].get("juicio") == "Acierto":
            casos_top1 += 1

        # Top 5: algun "Acierto" en posiciones 1-5
        acierto_en_top5 = any(
            j.get("juicio") == "Acierto"
            and j.get("posicion") in ("1", "2", "3", "4", "5")
            for j in juicios
        )
        if acierto_en_top5:
            casos_top5 += 1

        # Utilidad: cuantos de los 5 recibieron "Acierto" o "Sirve"
        utiles = sum(
            1 for j in juicios
            if j.get("juicio") in ("Acierto", "Sirve")
            and j.get("posicion") in ("1", "2", "3", "4", "5")
        )
        suma_utilidad += utiles

        # Estadisticas por tipo
        if tipo not in tipo_stats:
            tipo_stats[tipo] = {"total": 0, "top1": 0, "top5": 0, "suma_utilidad": 0.0}
        tipo_stats[tipo]["total"] += 1
        if pos1 and pos1[0].get("juicio") == "Acierto":
            tipo_stats[tipo]["top1"] += 1
        if acierto_en_top5:
            tipo_stats[tipo]["top5"] += 1
        tipo_stats[tipo]["suma_utilidad"] += utiles

    # Calcular porcentajes por tipo
    por_tipo = {}
    for tipo, stats in tipo_stats.items():
        n = stats["total"]
        por_tipo[tipo] = {
            "total": n,
            "top1": round(100 * stats["top1"] / n, 1) if n else 0.0,
            "top5": round(100 * stats["top5"] / n, 1) if n else 0.0,
            "utilidad": round(stats["suma_utilidad"] / n, 2) if n else 0.0,
        }

    return {
        "total_casos_evaluados": total_casos,
        "top1": round(100 * casos_top1 / total_casos, 1) if total_casos else 0.0,
        "top5": round(100 * casos_top5 / total_casos, 1) if total_casos else 0.0,
        "utilidad": round(suma_utilidad / total_casos, 2) if total_casos else 0.0,
        "por_tipo": por_tipo,
    }


# ── Endpoints de la API del buscador (proxy) ───────────────────────────────

@app.get("/health")
def health():
    """Proxy a GET /health de la API principal."""
    try:
        resp = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return resp.json()
    except requests.ConnectionError:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "detail": f"No se pudo conectar a la API en {API_BASE_URL}. "
                          "Levanta la API con: uvicorn api.main:app --host 0.0.0.0 --port 8000",
            },
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})


# ── Endpoints de casos ─────────────────────────────────────────────────────

@app.get("/api/casos")
def listar_casos():
    """Lista los casos de prueba disponibles."""
    casos = _leer_casos()
    total = len(casos)
    return {
        "total": total,
        "casos": [
            {
                "caso": c["caso"],
                "id_correcto": c["id_correcto"],
                "tipo": c.get("tipo", "desconocido"),
                "imagen": str(_imagen_caso_path(c["caso"]).name),
            }
            for c in casos
        ],
    }


@app.get("/api/casos/{n}")
def obtener_caso(n: int):
    """
    Devuelve el caso N (1-indexed) con los 5 resultados del buscador.
    Llama a POST /search/image de la API principal.
    """
    casos = _leer_casos()
    if n < 1 or n > len(casos):
        raise HTTPException(status_code=404, detail=f"Caso {n} no existe (total: {len(casos)})")

    caso = casos[n - 1]
    ruta_imagen = _imagen_caso_path(caso["caso"])

    if not ruta_imagen.exists():
        raise HTTPException(
            status_code=500,
            detail=f"No se encontro la imagen del caso: {ruta_imagen}",
        )

    # Llamar a la API principal para buscar resultados
    resultados_busqueda = []
    api_ok = False
    error_api = None
    try:
        with open(ruta_imagen, "rb") as img_file:
            files = {"file": (ruta_imagen.name, img_file, "image/jpeg")}
            data = {"modo": "auto", "modelo": "clip"}
            resp = requests.post(
                f"{API_BASE_URL}/search/image",
                files=files,
                data=data,
                timeout=60,
            )
            if resp.status_code == 200:
                api_data = resp.json()
                resultados_busqueda = api_data.get("resultados", [])
                api_ok = True
            else:
                error_api = f"API respondio {resp.status_code}: {resp.text[:200]}"
    except requests.ConnectionError:
        error_api = f"No se pudo conectar a la API en {API_BASE_URL}"
    except Exception as e:
        error_api = str(e)

    return {
        "caso": caso["caso"],
        "numero": n,
        "total": len(casos),
        "id_correcto": caso["id_correcto"],
        "tipo": caso.get("tipo", "desconocido"),
        "imagen": str(ruta_imagen.name),
        "imagen_ruta": str(ruta_imagen),
        "api_ok": api_ok,
        "error_api": error_api,
        "resultados": resultados_busqueda,
    }


# ── Endpoints de juicios ───────────────────────────────────────────────────

@app.post("/api/juicios")
def guardar_juicio(
    caso: str = Form(...),
    id_correcto: str = Form(...),
    posicion: str = Form(...),
    id_resultado: str = Form(...),
    score: str = Form(...),
    juicio: str = Form(...),
    quien: str = Form(""),
):
    """
    Guarda un juicio (clic de boton) en resultados.csv.
    Se guarda INMEDIATAMENTE en disco (append).
    """
    if juicio not in ("Acierto", "Sirve", "No sirve"):
        raise HTTPException(
            status_code=400,
            detail=f"Juicio invalido: '{juicio}'. Valores validos: Acierto, Sirve, No sirve",
        )

    fila = {
        "caso": caso,
        "id_correcto": id_correcto,
        "posicion": posicion,
        "id_resultado": id_resultado,
        "score": score,
        "juicio": juicio,
        "quien": quien,
        "fecha": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    }

    _guardar_juicio(fila)

    return {"ok": True, "mensaje": "Juicio guardado", "fila": fila}


# ── Endpoints de resultados y estadisticas ─────────────────────────────────

@app.get("/api/resultados")
def exportar_resultados():
    """Devuelve todo el contenido de resultados.csv."""
    resultados = _leer_resultados()
    return {
        "total": len(resultados),
        "columnas": RESULTADOS_COLUMNS,
        "resultados": resultados,
    }


@app.get("/api/resultados/csv")
def descargar_resultados_csv():
    """Descarga resultados.csv como archivo."""
    if not RESULTADOS_CSV.exists():
        raise HTTPException(status_code=404, detail="No hay resultados guardados aun")
    return FileResponse(
        path=str(RESULTADOS_CSV),
        media_type="text/csv",
        filename="resultados.csv",
    )


@app.get("/api/estadisticas")
def estadisticas():
    """Calcula y devuelve Top 1, Top 5 y Utilidad (total y por tipo)."""
    resultados = _leer_resultados()
    return _calcular_estadisticas(resultados)


@app.post("/api/reset")
def reset_resultados():
    """Limpia resultados.csv para re-evaluar."""
    if RESULTADOS_CSV.exists():
        RESULTADOS_CSV.unlink()
    return {"ok": True, "mensaje": "resultados.csv eliminado. Puedes volver a evaluar."}


# ── Frontend estatico ─────────────────────────────────────────────────────

# Servir archivos estaticos del frontend (Andres los creara aqui)
# Se monta al final para que no tape los endpoints anteriores.
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


# ── Punto de entrada ───────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("EVALUADOR DEL BUSCADOR — Ficha 03-A")
    print("=" * 60)
    print(f"Backend corriendo en:  http://127.0.0.1:{EVALUADOR_PORT}")
    print(f"API del buscador:      {API_BASE_URL}")
    print(f"Casos de prueba:       {CASOS_CSV}")
    print(f"Resultados se guardan: {RESULTADOS_CSV}")
    print("=" * 60)

    # Verificar que la API esta viva
    try:
        resp = requests.get(f"{API_BASE_URL}/health", timeout=3)
        info = resp.json()
        print(f"[OK] API conectada: {info.get('products', '?')} productos, "
              f"{info.get('embeddings', '?')} embeddings")
    except Exception:
        print(f"[AVISO] No se pudo conectar a la API en {API_BASE_URL}")
        print("        La API del buscador debe estar corriendo para evaluar.")
        print("        Levantala con: uvicorn api.main:app --host 0.0.0.0 --port 8000")

    uvicorn.run(app, host="0.0.0.0", port=EVALUADOR_PORT, reload=False)
