import os
import uuid
import numpy as np
from PIL import Image
import torch

# -------------------------------------------------------------------------
# IMPORTANTE: Aquí importamos el Vision Pipeline de tu Buscador.
# Debes asegurarte de copiar la carpeta 'core' de tu Buscador a RAG-V2,
# o ajustar las rutas para que encuentre YOLO, Rembg y Fashion-CLIP.
# -------------------------------------------------------------------------
from core.vision_pipeline import VisionPipeline
from core.base_datos import QdrantManager
from core.search_service import perform_hybrid_search

# Instancias Globales
pipeline = None
qdrant_db = None

# Colección del banco de imágenes propio (se indexa con
# scripts/indexar_banco_propio.py). Ya NO se usa la colección de Aimari
# (camisetas_fashion_v3) ni su migración automática desde embeddings.npy.
COLECCION_BANCO = "banco_propio_v1"

def cargar_indice():
    """
    Inicializa la conexión con Qdrant y carga los modelos de IA en memoria.
    Apunta a la colección del banco propio (banco_propio_v1), que se puebla
    con scripts/indexar_banco_propio.py.
    """
    global pipeline, qdrant_db
    print("Inicializando Motor de IA (YOLO + Rembg + SigLIP)...")
    pipeline = VisionPipeline()

    print(f"Conectando a Qdrant (colección: {COLECCION_BANCO})...")
    qdrant_db = QdrantManager(collection_name=COLECCION_BANCO)

    total = qdrant_db.client.count(qdrant_db.collection_name).count
    print(f"Colección '{COLECCION_BANCO}' lista con {total} vectores.")
    if total == 0:
        print(
            "AVISO: la colección está vacía. Indexá tu banco con: "
            "python scripts/indexar_banco_propio.py"
        )

    print("Sistemas operativos. Motor de búsqueda listo.")

def search_similar(imagen: Image.Image, color_filtro: str = None, top_k: int = 5):
    """
    Recibe una imagen (PIL), la procesa (YOLO+Rembg+CLIP), y busca en Qdrant.
    Si se proporciona un color_filtro, hace búsqueda híbrida exacta.
    """
    if pipeline is None or qdrant_db is None:
        raise RuntimeError("El índice no ha sido cargado. Llama a cargar_indice() primero.")
    
    # 1. Pipeline de Inteligencia Artificial (Extrae embedding y color)
    resultado = pipeline.process_image(imagen)
    query_vector = resultado["embedding"]
    color_detectado = resultado["color"]
    
    # Si el usuario no forzó un filtro de color, usamos el detectado
    color_a_filtrar = color_filtro if color_filtro else color_detectado
    
    # 2. Búsqueda Híbrida Vectorial en Qdrant (Traemos 30 para el Reranking)
    resultados_db = perform_hybrid_search(qdrant_db, query_vector, color_a_filtrar, limit=30)
    
    # 3. Formatear la salida para la API
    resultados_formateados = []
    for pos, r in enumerate(resultados_db, start=1):
        filename = r.payload.get("filename", "")
        original_id = r.payload.get("original_id", str(r.id))
        resultados_formateados.append({
            "id": original_id,
            "nombre": filename.split('.')[0] if filename else f"Producto {original_id}",
            "imagen": filename,
            "url": "",
            "proveedor": "Banco propio",
            "score": round(float(r.score), 4),
        })
        
    # 4. Reranking Visual (Corrige el problema de colores usando Hito 2)
    from api.search_engine_hito2 import _rerank_candidatos
    
    resultados_finales = _rerank_candidatos(
        candidatos=resultados_formateados,
        query_image=imagen,
        etiqueta_modelo="YOLO+SigLIP",
        top_k=top_k
    )
    
    return {
        "color_detectado": color_detectado,
        "resultados": resultados_finales
    }

def ingest_to_qdrant(imagen: Image.Image, filename: str):
    """
    (Opcional) Usa esta función para llenar tu base de datos Qdrant
    dinámicamente sin usar scripts estáticos de numpy.
    """
    resultado = pipeline.process_image(imagen)
    query_vector = resultado["embedding"]
    color = resultado["color"]
    
    from qdrant_client.http.models import PointStruct
    
    point_id = str(uuid.uuid4())
    point = PointStruct(
        id=point_id,
        vector=query_vector.tolist(),
        payload={"filename": filename, "color": color}
    )
    qdrant_db.upsert_vectors([point])
    return point_id

def info_indice() -> dict:
    """Retorna información del estado de Qdrant."""
    if qdrant_db is None:
        return {"status": "No inicializado"}
    # Podrías agregar una llamada a qdrant_db.client.count() aquí si lo deseas
    return {"status": "Qdrant Online", "coleccion": qdrant_db.collection_name}
