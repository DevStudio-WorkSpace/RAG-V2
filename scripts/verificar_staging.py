"""Prueba de integración para una copia aislada de staging.

Ejecutar dentro de API, con el stack completo iniciado. No imprime secretos.
No indexa ni modifica el catálogo; las búsquedas auto generan consultas locales.
"""

import io
import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from PIL import Image


def main():
    base = os.getenv("STAGING_TEST_URL", "http://proxy").rstrip("/")
    api = "http://localhost:8000"
    root = Path(__file__).resolve().parent.parent
    rows = pd.read_csv(root / "data/products.csv")
    ids = np.load(root / "data/ids.npy", allow_pickle=True).astype(str)
    results = []

    def check(name, ok, detail):
        results.append({"prueba": name, "ok": bool(ok), "detalle": detail})
        print(json.dumps(results[-1], ensure_ascii=False), flush=True)

    check("orden_ids", np.array_equal(ids, rows["id"].astype(str).values), len(ids))
    for name in ("embeddings", "embeddings_clip", "embeddings_openclip", "embeddings_siglip"):
        vectors = np.load(root / f"data/{name}.npy")
        check(name, len(vectors) == len(rows) and np.isfinite(vectors).all()
              and (np.linalg.norm(vectors, axis=1) > 0).all(), list(vectors.shape))

    client = {"X-API-Key": os.environ["API_CLIENT_KEY"]}
    r = requests.get(f"{base}/api/health", timeout=30)
    data = r.json()
    check("salud_proxy", r.status_code == 200 and not data.get("desfase_detectado", True)
          and data.get("products") == len(rows), data)
    r = requests.get(base, timeout=30)
    check("frontend", r.status_code == 200, r.status_code)

    image = root / "data/consultas/SBX-01-0001_exacta.jpg"
    for label, headers, expected in (("sin_clave", {}, 401), ("clave_invalida", {"X-API-Key": "invalid-staging-key"}, 401)):
        with image.open("rb") as f:
            r = requests.post(f"{api}/search/image", headers=headers,
                              files={"file": (image.name, f, "image/jpeg")}, timeout=30)
        check(label, r.status_code == expected, r.status_code)
    r = requests.get(f"{api}/health/qdrant", headers=client, timeout=30)
    check("cliente_sin_rol_admin", r.status_code == 403, r.status_code)

    tiny = io.BytesIO()
    Image.new("RGB", (16, 16)).save(tiny, format="PNG")
    for label, filename, content, mime in (
        ("archivo_invalido", "invalid.jpg", b"not an image", "image/jpeg"),
        ("imagen_pequena", "tiny.png", tiny.getvalue(), "image/png"),
    ):
        r = requests.post(f"{base}/api/search", files={"file": (filename, content, mime)}, timeout=30)
        check(label, r.status_code == 400, {"status": r.status_code, "body": r.text[:250]})

    r = requests.post(f"{base}/api/search", data={"modo": "original"}, timeout=30)
    check("sin_archivo", r.status_code == 400, r.status_code)

    for mode in ("original", "auto"):
        start = time.perf_counter()
        with image.open("rb") as f:
            r = requests.post(f"{base}/api/search", data={"modo": mode, "modelo": "clip"},
                              files={"file": (image.name, f, "image/jpeg")}, timeout=180)
        payload = r.json()
        matches = payload.get("resultados", []) if isinstance(payload, dict) else payload
        top = matches[0] if matches else {}
        check(f"busqueda_{mode}", r.status_code == 200 and top.get("id") == "SBX-01-0001",
              {"status": r.status_code, "segundos": round(time.perf_counter() - start, 3),
               "top1": top.get("id"), "resultados": len(matches), "error": payload.get("error") if isinstance(payload, dict) else None})

    r = requests.get(f"{base}/api/images/{rows.iloc[0]['imagen']}", timeout=30)
    check("imagen_frontend", r.status_code == 200 and r.headers.get("content-type", "").startswith("image/"), r.status_code)
    check("api_sigue_activa", requests.get(f"{api}/health", timeout=30).status_code == 200, "GET /health")
    print(json.dumps({"total": len(results), "correctas": sum(x["ok"] for x in results)}, ensure_ascii=False))
    return 0 if all(x["ok"] for x in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
