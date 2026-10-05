import os
import csv
import re
import sys
import uuid
import numpy as np
import argparse
from PIL import Image

# Configurar imports del proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from core.vision_pipeline import VisionPipeline
from core.base_datos import QdrantManager
from qdrant_client.http.models import PointStruct

def process_sublitex(image_folder, csv_path):
    print("Iniciando cargador de indexación para Sublitex...")
    
    # Validar entradas
    if not os.path.exists(image_folder):
        print(f"Error: No se encontró la carpeta de imágenes en {image_folder}")
        return
    if not os.path.exists(csv_path):
        print(f"Error: No se encontró el archivo CSV de control en {csv_path}")
        return

    # Leer CSV y crear mapa de metadatos
    metadata_map = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Esperamos que tenga al menos: codigo, carpeta_origen, archivo_original
            codigo = row.get("codigo", "").strip()
            if codigo:
                metadata_map[codigo] = {
                    "codigo": codigo,
                    "carpeta_origen": row.get("carpeta_origen", ""),
                    "archivo_original": row.get("archivo_original", "")
                }
    print(f"Cargados {len(metadata_map)} registros de metadatos desde CSV.")

    # Expresión regular para validar el código del archivo
    # Ej: SBX-12-1234
    regex_valido = re.compile(r"^SBX-\d{2}-\d{4}$")
    
    pipeline = VisionPipeline()
    vectores = []
    ids = []
    puntos_qdrant = []
    errores_log = []

    # Iterar sobre las imágenes de la carpeta
    archivos = [f for f in os.listdir(image_folder) if f.lower().endswith(".png")]
    print(f"Encontrados {len(archivos)} archivos PNG para procesar.")

    for filename in archivos:
        codigo = os.path.splitext(filename)[0]
        
        # Filtro de validación
        if not regex_valido.match(codigo):
            error_msg = f"Rechazado (nomenclatura inválida): {filename}"
            print(error_msg)
            errores_log.append(error_msg)
            continue
            
        ruta_imagen = os.path.join(image_folder, filename)
        
        try:
            imagen = Image.open(ruta_imagen).convert("RGB")
            resultado = pipeline.process_image(imagen)
            vector = resultado["embedding"]
            
            # Enriquecimiento con metadata
            meta = metadata_map.get(codigo, {
                "codigo": codigo,
                "carpeta_origen": "Desconocida",
                "archivo_original": filename
            })
            
            # Generar UUID para Qdrant (usando el código como semilla para consistencia)
            point_id = str(uuid.uuid5(uuid.NAMESPACE_OID, codigo))
            
            puntos_qdrant.append(
                PointStruct(
                    id=point_id,
                    vector=vector.tolist(),
                    payload=meta
                )
            )
            vectores.append(vector)
            ids.append(codigo)
            print(f"Procesado correctamente: {codigo}")
            
        except Exception as e:
            error_msg = f"Error procesando {filename}: {e}"
            print(error_msg)
            errores_log.append(error_msg)

    # Comprobación de integridad
    if len(vectores) != len(ids):
        print(f"ALERTA CRÍTICA: La longitud de vectores ({len(vectores)}) no coincide con la longitud de IDs ({len(ids)}). Abortando exportación.")
        sys.exit(1)
        
    if not vectores:
        print("No se procesaron vectores válidos.")
        sys.exit(1)

    print("Comprobación de integridad exitosa: longitud(vectores) == longitud(IDs).")

    # Aislamiento: Colección independiente
    collection_name = "sublitex_fashion_v1"
    print(f"Persistiendo en Qdrant (colección: {collection_name})...")
    
    qdrant_manager = QdrantManager(collection_name=collection_name)
    qdrant_manager.upsert_vectors(puntos_qdrant)
    
    # También persistimos en local como respaldo
    np.save(os.path.join(BASE_DIR, "data", "embeddings_sublitex.npy"), np.array(vectores, dtype=np.float32))
    np.save(os.path.join(BASE_DIR, "data", "ids_sublitex.npy"), np.array(ids))

    print(f"\nFinalizado exitosamente. Se insertaron {len(vectores)} vectores.")
    if errores_log:
        print("\nLog de errores:")
        for err in errores_log:
            print("-", err)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline de Indexación Sublitex")
    parser.add_argument("--image_folder", type=str, required=True, help="Ruta a la carpeta con archivos PNG")
    parser.add_argument("--csv_path", type=str, required=True, help="Ruta al archivo CSV de Control de exportación")
    args = parser.parse_args()
    
    process_sublitex(args.image_folder, args.csv_path)
