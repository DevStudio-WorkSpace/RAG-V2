"""
Evaluador Ficha 03-B
--------------------
Consume RAG-V2 por HTTP y permite evaluar los resultados con juicios humanos.
No modifica ningún archivo de RAG-V2.
"""

import csv
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import streamlit as st

st.set_page_config(
    page_title="Evaluador Ficha 03-B",
    layout="wide",
)

# =============================================================================
# RUTAS (calculadas desde la ubicación de app.py)
# =============================================================================
APP_DIR = Path(__file__).parent.resolve()
RAG_BASE = APP_DIR.parent.resolve()  # RAG-V2 raíz
CASOS_CSV = APP_DIR / "casos" / "casos.csv"
CASOS_FOTOS = APP_DIR / "casos" / "fotos"
CATALOGO_IMAGES = RAG_BASE / "data" / "images_normalized"
JUICIOS_JSONL = APP_DIR / "data" / "juicios.jsonl"
API_URL = "http://localhost:8000"

# Crear carpeta data/ si no existe (necesario para juicios.jsonl)
(APP_DIR / "data").mkdir(parents=True, exist_ok=True)

# =============================================================================
# RESOLVER RUTA DE IMAGEN DEL CATÁLOGO
# =============================================================================
def _resolver_ruta_catalogo(img_nombre, id_producto=""):
    """
    Devuelve la ruta de la imagen en el catálogo, probando diferentes
    extensiones ya que la normalización puede haberlas convertido a .jpg.
    """
    if not img_nombre:
        return Path()
    ruta = CATALOGO_IMAGES / img_nombre
    if ruta.exists():
        return ruta
    base = img_nombre.rsplit(".", 1)[0] if "." in img_nombre else img_nombre
    for ext in (".jpg", ".png", ".gif"):
        if id_producto:
            cand = CATALOGO_IMAGES / f"{id_producto}{ext}"
            if cand.exists():
                return cand
        cand = CATALOGO_IMAGES / f"{base}{ext}"
        if cand.exists():
            return cand
    return ruta

# =============================================================================
# CARGAR CASOS DESDE CSV
# =============================================================================
def cargar_casos():
    if not CASOS_CSV.exists():
        return []
    with open(CASOS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

# =============================================================================
# CARGAR JUICIOS DESDE JSONL
# =============================================================================
def cargar_juicios():
    if not JUICIOS_JSONL.exists():
        return {}
    juicios = {}
    with open(JUICIOS_JSONL, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            try:
                j = json.loads(linea)
                clave = (j.get("caso_id", ""), j.get("posicion", 0))
                juicios[clave] = j
            except json.JSONDecodeError:
                continue
    return juicios

# =============================================================================
# GUARDAR JUICIO EN JSONL (actualiza si ya existe caso_id + posicion)
# =============================================================================
def guardar_juicio(juicio):
    juicios = []
    existe = False
    if JUICIOS_JSONL.exists():
        with open(JUICIOS_JSONL, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    j = json.loads(linea)
                    if (j.get("caso_id") == juicio["caso_id"] and
                        j.get("posicion") == juicio["posicion"]):
                        juicios.append(juicio)
                        existe = True
                    else:
                        juicios.append(j)
                except json.JSONDecodeError:
                    continue

    if not existe:
        juicios.append(juicio)

    with open(JUICIOS_JSONL, "w", encoding="utf-8") as f:
        for j in juicios:
            f.write(json.dumps(j, ensure_ascii=False) + "\n")

# =============================================================================
# CONSULTAR RAG-V2 POR HTTP
# =============================================================================
def consultar_rag(foto_path):
    if not foto_path.exists():
        return None, f"La foto no existe: {foto_path}"

    try:
        with open(foto_path, "rb") as f:
            files = {"file": (foto_path.name, f, "image/jpeg")}
            data = {"modo": "clasico", "modelo": "clip"}
            resp = requests.post(
                f"{API_URL}/search/image",
                files=files,
                data=data,
                timeout=180,
            )
    except requests.exceptions.ConnectionError:
        return None, "No se pudo conectar a RAG-V2. Ejecuta: uvicorn api.main:app --port 8000"
    except requests.exceptions.Timeout:
        return None, "La consulta tardó demasiado."

    if resp.status_code != 200:
        try:
            err = resp.json().get("error", resp.text[:300])
        except Exception:
            err = resp.text[:300]
        return None, f"Error de API ({resp.status_code}): {err}"

    result = resp.json()
    resultados = result.get("resultados", [])
    if not resultados:
        return None, "La API no devolvió resultados."
    return resultados[:5], None

# =============================================================================
# CALCULAR MÉTRICAS DESDE JUICIOS
# =============================================================================
def calcular_metricas(juicios, casos):
    if not juicios:
        return None, None, None, 0

    casos_ids = [c["caso_id"] for c in casos]
    casos_evaluados = set()
    for clave in juicios:
        caso_id, _ = clave
        casos_evaluados.add(caso_id)

    total_casos = len(casos_evaluados)
    if total_casos == 0:
        return 0.0, 0.0, 0.0, 0

    top1_aciertos = 0
    top5_aciertos = 0
    utilidad_total = 0.0

    for caso_id in casos_evaluados:
        juicios_caso = {
            pos: j["juicio"].lower()
            for (cid, pos), j in juicios.items()
            if cid == caso_id
        }

        if 1 in juicios_caso and juicios_caso[1] == "acierto":
            top1_aciertos += 1

        if any(j in ("acierto",) for j in juicios_caso.values()):
            top5_aciertos += 1

        util = sum(1 for j in juicios_caso.values() if j in ("acierto", "sirve"))
        utilidad_total += util

    top1 = top1_aciertos / total_casos
    top5 = top5_aciertos / total_casos
    utilidad = utilidad_total / total_casos

    return top1, top5, utilidad, total_casos

# =============================================================================
# MÉTRICAS POR TIPO
# =============================================================================
def calcular_metricas_por_tipo(juicios, casos):
    tipos = {}
    for c in casos:
        tid = c.get("tipo", "desconocido")
        if tid not in tipos:
            tipos[tid] = {"casos": [], "juicios": {}}
        tipos[tid]["casos"].append(c["caso_id"])

    for clave, j in juicios.items():
        caso_id, pos = clave
        for tid, data in tipos.items():
            if caso_id in data["casos"]:
                data["juicios"][pos] = j["juicio"].lower()
                break

    resultados = {}
    for tid, data in tipos.items():
        casos_ids = data["casos"]
        juicios_map = data["juicios"]

        casos_evaluados = set()
        for (cid, _), j in juicios.items():
            if cid in casos_ids:
                casos_evaluados.add(cid)

        n = len(casos_evaluados)
        if n == 0:
            resultados[tid] = {"top1": 0.0, "top5": 0.0, "utilidad": 0.0, "n": 0}
            continue

        top1 = 0.0
        top5 = 0.0
        utilidad = 0.0

        for caso_id in casos_evaluados:
            juicios_caso = {
                pos: ju["juicio"].lower()
                for (cid, pos), ju in juicios.items()
                if cid == caso_id
            }
            if 1 in juicios_caso and juicios_caso[1] == "acierto":
                top1 += 1
            if any(j in ("acierto",) for j in juicios_caso.values()):
                top5 += 1
            util = sum(1 for j in juicios_caso.values() if j in ("acierto", "sirve"))
            utilidad += util

        resultados[tid] = {
            "top1": top1 / n,
            "top5": top5 / n,
            "utilidad": utilidad / n,
            "n": n,
        }

    return resultados

# =============================================================================
# INICIALIZAR ESTADO DE SESIÓN
# =============================================================================
def inicializar_estado():
    if "casos" not in st.session_state:
        casos = cargar_casos()
        st.session_state["casos"] = casos

    if "juicios" not in st.session_state:
        st.session_state["juicios"] = cargar_juicios()

    if "caso_actual" not in st.session_state:
        casos = st.session_state["casos"]
        juicios = st.session_state["juicios"]
        caso_actual = 0
        if casos:
            for i, c in enumerate(casos):
                cid = c["caso_id"]
                tiene_juicio = any(k[0] == cid for k in juicios)
                if not tiene_juicio:
                    caso_actual = i
                    break
        st.session_state["caso_actual"] = caso_actual

# =============================================================================
# INTERFAZ PRINCIPAL
# =============================================================================
def main():
    inicializar_estado()

    casos = st.session_state["casos"]
    juicios = st.session_state["juicios"]
    caso_actual = st.session_state["caso_actual"]

    st.title("EVALUADOR FICHA 03-B")

    if not casos:
        st.error(f"No se encontró casos.csv en: {CASOS_CSV}")
        st.stop()

    if caso_actual >= len(casos):
        caso_actual = 0
        st.session_state["caso_actual"] = 0

    caso = casos[caso_actual]
    cid = caso["caso_id"]
    foto_nombre = caso["foto"]
    tipo = caso["tipo"]
    foto_path = CASOS_FOTOS / foto_nombre

    n_total = len(casos)
    n_evaluados = len(set(k[0] for k in juicios if k[0] in [c["caso_id"] for c in casos]))

    col_nav = st.columns([1, 1, 4, 1, 1])
    with col_nav[0]:
        if st.button("Anterior", disabled=(caso_actual == 0), use_container_width=True):
            st.session_state["caso_actual"] = caso_actual - 1
            st.rerun()
    with col_nav[1]:
        if st.button("Siguiente", disabled=(caso_actual >= n_total - 1), use_container_width=True):
            st.session_state["caso_actual"] = caso_actual + 1
            st.rerun()

    st.markdown(f"**Caso {caso_actual + 1} / {n_total}** — `{cid}` — Tipo: `{tipo}` — Evaluados: {n_evaluados}/{n_total}")

    # =========================================================================
    # MOSTRAR FOTO DEL CASO
    # =========================================================================
    if foto_path.exists():
        st.image(str(foto_path), caption=f"Foto del caso: {foto_nombre}", width=300)
    else:
        st.error(f"Falta la foto del caso: {foto_path}")

    # =========================================================================
    # CONSULTAR RAG-V2
    # =========================================================================
    resultados = None
    error = None

    if foto_path.exists():
        with st.spinner("Consultando RAG-V2..."):
            resultados, error = consultar_rag(foto_path)

    if error:
        st.error(error)
        return

    if resultados is None:
        st.warning("No hay resultados para mostrar.")
        return

    # =========================================================================
    # MOSTRAR RESULTADOS
    # =========================================================================
    st.markdown("---")
    st.markdown("**RESULTADOS**")

    for i, r in enumerate(resultados, start=1):
        rid = r.get("id", "")
        nombre = r.get("nombre", "")
        score = r.get("score", 0.0)
        img_cat = r.get("imagen", "")
        img_path = _resolver_ruta_catalogo(img_cat, rid)

        juicio_existente = juicios.get((cid, i))

        with st.container():
            col_img, col_info, col_juicio = st.columns([1, 2, 2])

            with col_img:
                if img_path.exists():
                    st.image(str(img_path), width=150)
                else:
                    st.error(f"Imagen no encontrada: {img_path.name}")

            with col_info:
                st.markdown(f"**Resultado {i}**")
                st.markdown(f"ID: `{rid}`")
                st.markdown(f"Nombre: {nombre}")
                st.markdown(f"Score: {score:.4f}")

            with col_juicio:
                if juicio_existente:
                    j = juicio_existente["juicio"].upper()
                    st.success(f"Ya evaluado: **{j}**")

                st.markdown("¿Es el resultado correcto?")

                def registrar(tipo_j, pos=i, img=img_cat, rid_=rid, score_=score):
                    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                    juicio_data = {
                        "caso_id": cid,
                        "tipo": tipo,
                        "posicion": pos,
                        "id_resultado": rid_,
                        "juicio": tipo_j,
                        "score": score_,
                        "timestamp": ahora,
                    }
                    guardar_juicio(juicio_data)
                    st.session_state["juicios"] = cargar_juicios()
                    st.rerun()

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.button(
                        "ACIERTO",
                        key=f"acierto_{cid}_{i}",
                        on_click=registrar,
                        args=("acierto",),
                        use_container_width=True,
                    )
                with c2:
                    st.button(
                        "SIRVE",
                        key=f"sirve_{cid}_{i}",
                        on_click=registrar,
                        args=("sirve",),
                        use_container_width=True,
                    )
                with c3:
                    st.button(
                        "NO SIRVE",
                        key=f"nosirve_{cid}_{i}",
                        on_click=registrar,
                        args=("no_sirve",),
                        use_container_width=True,
                    )

        st.markdown("---")

    # =========================================================================
    # MÉTRICAS GLOBALES
    # =========================================================================
    casos_ids = [c["caso_id"] for c in casos]
    juicios_filtrados = {
        k: v for k, v in juicios.items()
        if k[0] in casos_ids
    }

    top1, top5, utilidad, n = calcular_metricas(juicios_filtrados, casos)

    st.markdown("---")
    st.markdown("### MÉTRICAS GLOBALES")
    if n > 0:
        st.markdown(f"- **Top 1:** {top1:.1%} ({int(top1 * n)}/{n})")
        st.markdown(f"- **Top 5:** {top5:.1%} ({int(top5 * n)}/{n})")
        st.markdown(f"- **Utilidad:** {utilidad:.2f} / 5")
    else:
        st.info("No hay juicios evaluados todavía.")

    # =========================================================================
    # MÉTRICAS POR TIPO
    # =========================================================================
    metricas_tipo = calcular_metricas_por_tipo(juicios_filtrados, casos)
    if metricas_tipo:
        st.markdown("### MÉTRICAS POR TIPO")
        for tid, m in metricas_tipo.items():
            n_t = m["n"]
            if n_t > 0:
                st.markdown(f"- **{tid}** ({n_t} casos): Top1={m['top1']:.1%}, Top5={m['top5']:.1%}, Utilidad={m['utilidad']:.2f}/5")
            else:
                st.markdown(f"- **{tid}** (0 casos evaluados)")

if __name__ == "__main__":
    main()
