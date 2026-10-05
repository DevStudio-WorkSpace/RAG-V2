import os
import csv
import time
import numpy as np
from PIL import Image
import sys

# Agregar el directorio base al path para poder importar desde core
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from core.vision_pipeline import VisionPipeline

DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "products.csv")
IMAGES_DIR = os.path.join(DATA_DIR, "images_normalized")
EMBEDDINGS_PATH = os.path.join(DATA_DIR, "embeddings_fashion.npy")
IDS_PATH = os.path.join(DATA_DIR, "ids_fashion.npy")

def resolver_ruta_imagen(fila):
    ruta = os.path.join(IMAGES_DIR, fila["imagen"])
    if os.path.exists(ruta):
        return ruta
    for candidata in (
        os.path.join(IMAGES_DIR, fila["id"] + ".jpg"),
        os.path.join(IMAGES_DIR, fila["id"] + ".png"),
        os.path.join(IMAGES_DIR, os.path.splitext(fila["imagen"])[0] + ".jpg"),
    ):
        if os.path.exists(candidata):
            return candidata
    return None

def main():
    print("Iniciando entrenamiento estricto del Motor Nuevo (YOLO + Rembg + Fashion-CLIP)...")
    pipeline = VisionPipeline()
    
    if not os.path.exists(CSV_PATH):
        print(f"Error: No se encontró {CSV_PATH}")
        return
        
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        filas = list(reader)
        
    total = len(filas)
    dimensiones = 768 # SigLIP output dimension
    
    embeddings = np.zeros((total, dimensiones), dtype=np.float32)
    ids = np.empty(total, dtype=object)
    
    # --- LÓGICA INCREMENTAL ---
    # Cargar embeddings previos si existen, para evitar reprocesar todo
    embeddings_previos = {}
    if os.path.exists(EMBEDDINGS_PATH) and os.path.exists(IDS_PATH):
        try:
            emb_viejos = np.load(EMBEDDINGS_PATH)
            ids_viejos = np.load(IDS_PATH, allow_pickle=True)
            for id_viejo, emb_viejo in zip(ids_viejos, emb_viejos):
                # Ignorar vectores que sean todo ceros (casos que fallaron antes)
                if np.any(emb_viejo): 
                    embeddings_previos[id_viejo] = emb_viejo
            print(f"Se cargaron {len(embeddings_previos)} imágenes previamente procesadas.")
        except Exception as e:
            print(f"No se pudieron cargar los embeddings previos: {e}")

    errores = 0
    inicio = time.perf_counter()
    
    print(f"Procesando {total} imágenes usando multithreading (memoria compartida)...")
    
    import concurrent.futures
    import threading

    procesados = 0
    saltados = 0
    lock = threading.Lock()

    def process_row(idx, fila):
        nonlocal errores, procesados, saltados
        product_id = fila["id"]
        ids[idx] = product_id
        
        # Si ya lo procesamos antes, copiamos el embedding y evitamos YOLO/CLIP
        if product_id in embeddings_previos:
            embeddings[idx] = embeddings_previos[product_id]
            with lock:
                saltados += 1
                procesados += 1
                if procesados % 100 == 0:
                    print(f"[{procesados}/{total}] (Usando {saltados} de caché previa...)")
            return

        
        ruta_imagen = resolver_ruta_imagen(fila)
        if not ruta_imagen:
            with lock:
                print(f"[{procesados}/{total}] Error: Imagen no encontrada para {product_id}")
                errores += 1
                procesados += 1
            return
            
        try:
            imagen = Image.open(ruta_imagen).convert("RGB")
            resultado = pipeline.process_image(imagen)
            embeddings[idx] = resultado["embedding"]
            
            with lock:
                procesados += 1
                if procesados % 10 == 0:
                    print(f"[{procesados}/{total}] Procesado. Último color: {resultado['color']}")
                
        except Exception as e:
            with lock:
                print(f"[{procesados}/{total}] Error procesando {product_id}: {e}")
                errores += 1
                procesados += 1

    # Usamos 4 hilos. Al ser hilos y no procesos, los modelos NO se duplican en la RAM.
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_row, idx, fila) for idx, fila in enumerate(filas)]
        concurrent.futures.wait(futures)
            
    # Guardamos los embeddings nuevos
    np.save(EMBEDDINGS_PATH, embeddings)
    np.save(IDS_PATH, ids)
    
    # Sobrescribimos embeddings.npy para que el evaluador viejo lo use
    np.save(os.path.join(DATA_DIR, "embeddings.npy"), embeddings)
    np.save(os.path.join(DATA_DIR, "ids.npy"), ids)
    
    # Borrar la DB de Qdrant para obligar a que se regenere con los nuevos embeddings
    qdrant_path = os.path.join(BASE_DIR, "qdrant_data")
    if os.path.exists(qdrant_path):
        import shutil
        shutil.rmtree(qdrant_path)
        print("Base de datos local de Qdrant limpiada para forzar regeneración.")

    tiempo = time.perf_counter() - inicio
    print(f"\nEntrenamiento finalizado en {tiempo:.2f}s")
    print(f"Errores: {errores}")
    print("El motor ahora está usando los vectores de Fashion-CLIP segmentados por YOLO.")

if __name__ == '__main__':
    main()
