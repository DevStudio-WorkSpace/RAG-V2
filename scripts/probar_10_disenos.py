import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_datos import QdrantManager
from core.vision_pipeline import VisionPipeline
from core.search_service import perform_hybrid_search
from PIL import Image
import cv2
import numpy as np

# Copiar las funciones necesarias de search_engine_hito2 para evitar problemas de importación
from api.descriptores_visuales import (
    descriptores_de_bgr,
    similitudes_visuales,
)

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CARPETA_IMAGENES = os.path.join(DATADIR, "images_normalized")

# Pesos del reranking
_PESOS = {
    "embedding": 0.50,
    "color_global": 0.07,
    "color_frente": 0.04,
    "color_espalda": 0.04,
    "estructura": 0.07,
    "color_dominante": 0.08,
    "gama": 0.04,
    "patron": 0.06,
    "marco": 0.06,
    "franjas": 0.04,
}
_total_pesos = sum(_PESOS.values())
PESOS = {k: v / _total_pesos for k, v in _PESOS.items()}

MARGEN_CORTE = 0.25
UMBRAL_MINIMO_SIMILARIDAD = 0.40
TAM_ESTRUCTURA = 32

_cache_descriptores = {}
_cache_descripciones_pre = {}
_cache_avanzados_online = {}

def _leer_bgr_desde_ruta(ruta):
    try:
        im = Image.open(ruta).convert("RGB")
    except Exception:
        return None
    return cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)

def _a_imagen_bgr(imagen):
    if imagen is None:
        return None
    if isinstance(imagen, (str, os.PathLike)):
        return _leer_bgr_desde_ruta(str(imagen))
    if hasattr(imagen, "convert"):
        try:
            arr = np.array(imagen.convert("RGB"))
        except Exception:
            return None
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    if isinstance(imagen, np.ndarray):
        return imagen
    return None

def _histograma_hsv(bgr):
    if bgr is None or bgr.size == 0:
        return None
    if bgr.ndim == 2:
        bgr = cv2.cvtColor(bgr, cv2.COLOR_GRAY2BGR)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    histograma = cv2.calcHist(
        [hsv], [0, 1, 2], None, [8, 8, 8], [0, 180, 0, 256, 0, 256]
    )
    cv2.normalize(histograma, histograma, 0, 1, cv2.NORM_MINMAX)
    return histograma

def _mitades_bgr(bgr):
    if bgr is None or bgr.size == 0:
        return None, None
    w = bgr.shape[1]
    return bgr[:, : w // 2], bgr[:, w // 2 :]

def _estructura_gris(bgr):
    if bgr is None or bgr.size == 0:
        return None
    if bgr.ndim == 3:
        gris = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    else:
        gris = bgr
    gris = cv2.resize(
        gris, (TAM_ESTRUCTURA, TAM_ESTRUCTURA), interpolation=cv2.INTER_AREA
    )
    return gris.astype(np.float32) / 255.0

def _correlacion_estructura(a, b):
    if a is None or b is None:
        return 0.0
    fa = a.ravel()
    fb = b.ravel()
    std_a, std_b = fa.std(), fb.std()
    if std_a < 1e-6 and std_b < 1e-6:
        return 1.0
    if std_a < 1e-6 or std_b < 1e-6:
        return 0.0
    corr = float(np.corrcoef(fa, fb)[0, 1])
    return max(0.0, min(1.0, corr))

def _sim_color(a, b):
    if a is None or b is None:
        return 0.0
    sim = float(cv2.compareHist(a, b, cv2.HISTCMP_CORREL))
    return max(0.0, min(1.0, sim))

def _resolver_imagen(nombre_archivo, id_catalogo=None):
    candidatas = [str(nombre_archivo)]
    if id_catalogo:
        candidatas.append(str(id_catalogo) + ".jpg")
    for nombre in candidatas:
        ruta = os.path.join(CARPETA_IMAGENES, nombre)
        if os.path.exists(ruta):
            return ruta
    return None

def _descriptores_de_archivo(nombre_archivo, id_catalogo=None):
    clave = (CARPETA_IMAGENES, str(nombre_archivo), str(id_catalogo))
    if clave in _cache_descriptores:
        return _cache_descriptores[clave]
    ruta = _resolver_imagen(nombre_archivo, id_catalogo)
    bgr = _leer_bgr_desde_ruta(ruta) if ruta else None
    if bgr is None:
        _cache_descriptores[clave] = None
        return None
    izq, der = _mitades_bgr(bgr)
    desc = {
        "hist_global": _histograma_hsv(bgr),
        "hist_frente": _histograma_hsv(izq),
        "hist_espalda": _histograma_hsv(der),
        "estructura": _estructura_gris(bgr),
        "avanzados": descriptores_de_bgr(bgr),
    }
    _cache_descriptores[clave] = desc
    return desc

def _descriptores_avanzados_candidato(cand):
    mapa = _cache_descripciones_pre
    if mapa is not None:
        desc = mapa.get(str(cand["id"]))
        if desc is not None:
            return desc
    key = (CARPETA_IMAGENES, str(cand["id"]))
    if key in _cache_avanzados_online:
        return _cache_avanzados_online[key]
    ruta = _resolver_imagen(cand["imagen"], cand["id"])
    bgr = _leer_bgr_desde_ruta(ruta) if ruta else None
    desc = descriptores_de_bgr(bgr) if bgr is not None else None
    _cache_avanzados_online[key] = desc
    return desc

def _rerank_candidatos_local(candidatos, query_image, etiqueta_modelo, top_k: int = 5):
    if not candidatos:
        return []
    
    scores_emb = np.array([c["score"] for c in candidatos], dtype=np.float64)
    smin, smax = float(scores_emb.min()), float(scores_emb.max())
    rango = smax - smin

    def _emb_norm(s):
        if rango < 1e-9:
            return 0.5
        return (s - smin) / rango

    bgr_consulta = _a_imagen_bgr(query_image)
    q_izq, q_der = _mitades_bgr(bgr_consulta)
    q_hist_global = _histograma_hsv(bgr_consulta)
    q_hist_frente = _histograma_hsv(q_izq)
    q_hist_espalda = _histograma_hsv(q_der)
    q_estructura = _estructura_gris(bgr_consulta)
    q_avanzados = descriptores_de_bgr(bgr_consulta)

    _es_recolor = False
    if q_hist_global is not None and len(candidatos) > 5:
        distancias_color = []
        for cand in candidatos[:10]:
            desc_cand = _descriptores_de_archivo(
                cand["imagen"], id_catalogo=cand.get("id")
            )
            if desc_cand is not None and desc_cand.get("hist_global") is not None:
                dist = cv2.compareHist(
                    q_hist_global, desc_cand["hist_global"], cv2.HISTCMP_CHISQR
                )
                distancias_color.append(dist)
        if distancias_color:
            dist_promedio = np.mean(distancias_color)
            if dist_promedio > 5.0:
                _es_recolor = True

    reranked = []
    for pos_inicial, cand in enumerate(candidatos, start=1):
        score_embedding = float(cand["score"])
        score_embedding_norm = _emb_norm(score_embedding)

        desc = _descriptores_de_archivo(cand["imagen"], id_catalogo=cand.get("id"))
        desc_av = _descriptores_avanzados_candidato(cand)
        if desc_av is None and desc is not None:
            desc_av = desc.get("avanzados")

        if desc is not None:
            score_color_global = _sim_color(q_hist_global, desc["hist_global"])
            score_frente = _sim_color(q_hist_frente, desc["hist_frente"])
            score_espalda = _sim_color(q_hist_espalda, desc["hist_espalda"])
            score_estructura = _correlacion_estructura(q_estructura, desc["estructura"])
        else:
            score_color_global = 0.0
            score_frente = 0.0
            score_espalda = 0.0
            score_estructura = 0.0

        if q_avanzados is not None and desc_av is not None:
            vis = similitudes_visuales(q_avanzados, desc_av)
            score_color_dominante = vis["color_dominante"]
            score_gama = vis["gama"]
            score_patron = vis["patron"]
            score_marco = vis["marco"]
            score_franjas = vis["franjas"]
        else:
            score_color_dominante = 0.0
            score_gama = 0.0
            score_patron = 0.0
            score_marco = 0.0
            score_franjas = 0.0

        if _es_recolor:
            _peso_emb = PESOS["embedding"] * 1.2
            _peso_color_g = PESOS["color_global"] * 0.5
            _peso_color_f = PESOS["color_frente"] * 0.5
            _peso_color_e = PESOS["color_espalda"] * 0.5
            _peso_estr = PESOS["estructura"] * 1.5
            _peso_color_d = PESOS["color_dominante"] * 0.5
            _peso_gama = PESOS["gama"] * 0.5
            _peso_patron = PESOS["patron"] * 1.5
            _peso_marco = PESOS["marco"] * 1.3
            _peso_franjas = PESOS["franjas"] * 1.3
        else:
            _peso_emb = PESOS["embedding"]
            _peso_color_g = PESOS["color_global"]
            _peso_color_f = PESOS["color_frente"]
            _peso_color_e = PESOS["color_espalda"]
            _peso_estr = PESOS["estructura"]
            _peso_color_d = PESOS["color_dominante"]
            _peso_gama = PESOS["gama"]
            _peso_patron = PESOS["patron"]
            _peso_marco = PESOS["marco"]
            _peso_franjas = PESOS["franjas"]

        score_final = (
            _peso_emb * score_embedding_norm
            + _peso_color_g * score_color_global
            + _peso_color_f * score_frente
            + _peso_color_e * score_espalda
            + _peso_estr * score_estructura
            + _peso_color_d * score_color_dominante
            + _peso_gama * score_gama
            + _peso_patron * score_patron
            + _peso_marco * score_marco
            + _peso_franjas * score_franjas
        )

        score_color = (
            PESOS["color_global"] * score_color_global
            + PESOS["color_frente"] * score_frente
            + PESOS["color_espalda"] * score_espalda
        ) / max(
            1e-9, PESOS["color_global"] + PESOS["color_frente"] + PESOS["color_espalda"]
        )

        reranked.append(
            {
                **cand,
                "score_inicial": round(score_embedding, 4),
                "score_recuperacion": round(score_embedding, 4),
                "posicion_inicial": pos_inicial,
                "score_embedding": round(score_embedding_norm, 4),
                "score_color_global": round(score_color_global, 4),
                "score_color_frente": round(score_frente, 4),
                "score_color_espalda": round(score_espalda, 4),
                "score_estructura": round(score_estructura, 4),
                "score_color_dominante": round(score_color_dominante, 4),
                "score_gama": round(score_gama, 4),
                "score_patron": round(score_patron, 4),
                "score_marco": round(score_marco, 4),
                "score_franjas": round(score_franjas, 4),
                "score_color": round(score_color, 4),
                "score_reranking": round(float(score_final), 4),
            }
        )

    reranked.sort(key=lambda r: r["score_reranking"], reverse=True)

    if reranked:
        reranked = [
            r for r in reranked if r["score_reranking"] >= UMBRAL_MINIMO_SIMILARIDAD
        ]
    if reranked:
        mejor_score = reranked[0]["score_reranking"]
        limite_corte = mejor_score - MARGEN_CORTE
        reranked = [r for r in reranked if r["score_reranking"] >= limite_corte]

    final = []
    for posicion, r in enumerate(reranked[:top_k], start=1):
        r["posicion_final"] = posicion
        r["modelo"] = etiqueta_modelo
        r["modelo_utilizado"] = (
            f"{etiqueta_modelo}+color+estructura+patron+marco+franjas"
        )
        final.append(r)

    return final

# 10 diseños de prueba
codigos_prueba = [
    'SBX-03-0001', 'SBX-03-0005', 'SBX-03-0010', 'SBX-03-0015',
    'SBX-03-0020', 'SBX-03-0025', 'SBX-03-0030', 'SBX-03-0035',
    'SBX-03-0040', 'SBX-03-0008'
]

print('=' * 80)
print('PRUEBA DE 10 DISEÑOS - BÚSQUEDA TOP 5 (Sublitex)')
print('=' * 80)

# Inicializar con colección de Sublitex
qdrant_db = QdrantManager(collection_name='sublitex_fashion_v1')
pipeline = VisionPipeline()

resultados_resumen = []

for codigo in codigos_prueba:
    img_path = f'data/demo_sublitex/png_publicados/{codigo}.png'
    img = Image.open(img_path).convert('RGB')
    resultado = pipeline.process_image(img)
    query_vector = resultado['embedding']
    color_detectado = resultado['color']
    
    # Buscar en Qdrant (recuperación amplia)
    resultados_db = perform_hybrid_search(qdrant_db, query_vector, color_detectado, limit=30)
    
    # Formatear candidatos para reranking
    candidatos = []
    for r in resultados_db:
        cand_codigo = r.payload.get('codigo', 'N/A')
        filename = r.payload.get('png', '')
        candidatos.append({
            'id': cand_codigo,
            'nombre': cand_codigo,
            'imagen': filename,
            'url': '',
            'proveedor': 'Sublitex',
            'score': float(r.score),
        })
    
    # Reranking visual (Hito 2)
    resultados_finales = _rerank_candidatos_local(candidatos, img, etiqueta_modelo='YOLO+SigLIP', top_k=5)
    
    print(f'\nConsulta: {codigo} (color detectado: {color_detectado})')
    print('-' * 80)
    for pos, r in enumerate(resultados_finales, start=1):
        print(f'  {pos}. {r["id"]} - score_inicial: {r["score_inicial"]:.4f} - score_reranking: {r["score_reranking"]:.4f} - modelo: {r["modelo_utilizado"]}')
    
    # Verificar si el código correcto está en Top 1 y Top 5
    top1 = resultados_finales[0]['id'] if resultados_finales else 'N/A'
    top5_ids = [r['id'] for r in resultados_finales]
    en_top1 = '✓' if top1 == codigo else '✗'
    en_top5 = '✓' if codigo in top5_ids else '✗'
    print(f'  Top 1 correcto: {en_top1} | Top 5 correcto: {en_top5}')
    
    resultados_resumen.append({
        'consulta': codigo,
        'color_detectado': color_detectado,
        'top1': top1,
        'top1_correcto': top1 == codigo,
        'top5_correcto': codigo in top5_ids,
        'top5_ids': top5_ids
    })

print('\n' + '=' * 80)
print('RESUMEN')
print('=' * 80)
top1_count = sum(1 for r in resultados_resumen if r['top1_correcto'])
top5_count = sum(1 for r in resultados_resumen if r['top5_correcto'])
print(f'Top 1 correcto: {top1_count}/10 ({top1_count*10}%)')
print(f'Top 5 correcto: {top5_count}/10 ({top5_count*10}%)')
print('\nDetalle:')
for r in resultados_resumen:
    print(f"  {r['consulta']}: Top1={r['top1']} ({'✓' if r['top1_correcto'] else '✗'}) | Top5={'✓' if r['top5_correcto'] else '✗'}")